import psycopg
from dotenv import load_dotenv
from psycopg.rows import dict_row
import os

load_dotenv()

def get_connection():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise RuntimeError("DATABASE_URL is not set")
    return psycopg.connect(db_url, row_factory=dict_row)

if __name__ == "__main__":
    query = "SELECT * FROM spotify_tokens"
    
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query=query)
            rows = cur.fetchall()
            print(rows)