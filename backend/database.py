import os
import json
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
        cursorclass=pymysql.cursors.DictCursor,
    )


def save_report(report: dict, attributes: dict, embedding: list[float]):
    """Storage requires the real schema; no INSERT columns are assumed here."""
    raise NotImplementedError(
        "Report processed but not saved: TiDB reports schema and INSERT mapping "
        "are not defined in the project."
    )

def search_similar_reports(target_type: str, query_vector: list[float], limit: int = 5):
    """Existing query; its table/columns still need verification against TiDB."""
    if target_type not in ("lost", "found") or limit < 1 or not query_vector:
        raise ValueError("Provide lost/found, a nonempty vector, and a positive limit")
    sql_query = """
        SELECT 
            id, 
            title, 
            category, 
            primary_color, 
            brand, 
            distinctive_features, 
            location_name,
            (1 - VEC_COSINE_DISTANCE(description_vector, %s)) AS vector_score
        FROM reports
        WHERE report_type = %s
        ORDER BY VEC_COSINE_DISTANCE(description_vector, %s) ASC
        LIMIT %s;
    """

    vector_str = json.dumps(query_vector, allow_nan=False)
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql_query, (vector_str, target_type, vector_str, limit))
            return cursor.fetchall()
    finally:
        conn.close()
