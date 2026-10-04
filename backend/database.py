import os
import json
import math
from datetime import datetime, timezone
from pathlib import Path
import pymysql
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")


def get_connection():
    """Open a TLS-verified connection only when a database operation needs it."""
    required = ("TIDB_HOST", "TIDB_USER", "TIDB_PASSWORD", "TIDB_DATABASE")
    missing = [name for name in required if not os.getenv(name)]
    if missing:
        raise ValueError("Missing TiDB configuration: " + ", ".join(missing))
    ca_path = Path(os.getenv("TIDB_SSL_CA") or "isrgrootx1.pem")
    if not ca_path.is_absolute():
        ca_path = Path(__file__).resolve().parent / ca_path
    return pymysql.connect(
        host=os.environ["TIDB_HOST"],
        port=int(os.getenv("TIDB_PORT", "4000")),
        user=os.environ["TIDB_USER"],
        password=os.environ["TIDB_PASSWORD"],
        database=os.environ["TIDB_DATABASE"],
        ssl_ca=str(ca_path),
        ssl_verify_cert=True,
        ssl_verify_identity=True,
        connect_timeout=10,
        read_timeout=30,
        write_timeout=30,
        init_command="SET time_zone = '+00:00'",
        cursorclass=pymysql.cursors.DictCursor,
    )


REPORT_COLUMNS = """
    id, report_type, title, description, image_url,
    category, primary_color, brand, model, distinctive_features, keywords,
    location_name, event_timestamp, created_at
"""


def vector_json(vector: list[float]) -> str:
    if len(vector) != 768 or not all(math.isfinite(value) for value in vector):
        raise ValueError("Embedding must contain exactly 768 finite numbers")
    if not any(vector):
        raise ValueError("Embedding cannot be a zero vector")
    return json.dumps(vector, allow_nan=False)


def decode_row(row):
    if row is None:
        return None
    row = dict(row)
    for key in ("distinctive_features", "keywords", "description_vector"):
        if key in row and isinstance(row[key], (str, bytes)):
            row[key] = json.loads(row[key])
    for key in ("distinctive_features", "keywords"):
        if key in row and row[key] is None:
            row[key] = []
    # TiDB DATETIME has no timezone. The API stores/reports timestamps in UTC.
    for key in ("event_timestamp", "created_at"):
        if isinstance(row.get(key), datetime) and row[key].tzinfo is None:
            row[key] = row[key].replace(tzinfo=timezone.utc)
    return row


def save_report(report: dict, attributes: dict, embedding: list[float]):
    """Insert the supplied schema, with JSON arrays and the 768D vector."""
    sql = """
        INSERT INTO reports (
            id, report_type, title, description, image_url,
            category, primary_color, brand, model, distinctive_features,
            keywords, location_name, description_vector, event_timestamp
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    timestamp = report["event_timestamp"]
    if timestamp.tzinfo is not None:
        timestamp = timestamp.astimezone(timezone.utc).replace(tzinfo=None)
    values = (
        report["id"], report["report_type"], report["title"],
        report["description"], report.get("image_url"),
        attributes.get("category"), attributes.get("primary_color"),
        attributes.get("brand"), attributes.get("model"),
        json.dumps(attributes.get("distinctive_features", [])),
        json.dumps(attributes.get("keywords", [])), report["location_name"],
        vector_json(embedding), timestamp,
    )
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, values)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
    return report["id"]


def get_reports(report_type=None, limit=50, offset=0):
    sql = f"SELECT {REPORT_COLUMNS} FROM reports"
    params = []
    if report_type is not None:
        sql += " WHERE report_type = %s"
        params.append(report_type)
    sql += " ORDER BY created_at DESC, id DESC LIMIT %s OFFSET %s"
    params.extend((limit, offset))
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, params)
            return [decode_row(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def get_report(report_id, include_vector=False):
    # Only this backend boolean controls column selection, never Gemini/user SQL.
    columns = REPORT_COLUMNS + (", description_vector" if include_vector else "")
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(f"SELECT {columns} FROM reports WHERE id = %s", (report_id,))
            return decode_row(cursor.fetchone())
    finally:
        conn.close()


def search_similar_reports(target_type: str, query_vector: list[float], limit: int = 5):
    """Lost-item matching is restricted to FOUND candidates."""
    if target_type.upper() != "FOUND" or not 1 <= limit <= 5:
        raise ValueError("Search only FOUND reports, with a limit from 1 to 5")
    sql_query = f"""
        SELECT {REPORT_COLUMNS},
            (1 - VEC_COSINE_DISTANCE(description_vector, %s)) AS vector_score
        FROM reports
        WHERE report_type = %s
        ORDER BY VEC_COSINE_DISTANCE(description_vector, %s) ASC
        LIMIT %s;
    """

    vector_str = vector_json(query_vector)
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql_query, (vector_str, "FOUND", vector_str, limit))
            return [decode_row(row) for row in cursor.fetchall()]
    finally:
        conn.close()
