import os
import json
import pymysql
from dotenv import load_dotenv

load_dotenv()

TIDB_CONFIG = {
    "host": os.getenv("TIDB_HOST"),
    "port": int(os.getenv("TIDB_PORT", 4000)),
    "user": os.getenv("TIDB_USER"),
    "password": os.getenv("TIDB_PASSWORD"),
    "database": os.getenv("TIDB_DATABASE"),
}

def search_similar_reports(target_type: str, query_vector: list[float], limit: int = 5):
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

# Formats the list cleanly into valid JSON array format '[0.1, 0.2, ...]'
vector_str = json.dumps(query_vector)

conn = pymysql.connect(**TIDB_CONFIG, cursorclass=pymysql.cursors.DictCursor)
try:
    with conn.cursor() as cursor:
        cursor.execute(sql_query, (vector_str, target_type, vector_str, limit))
        return cursor.fetchall()
finally:
    conn.close()