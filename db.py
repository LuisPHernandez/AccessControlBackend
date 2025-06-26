import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()

    # Create the user table if it doesn't exist
    cur.execute("""
        CREATE TABLE IF NOT EXISTS "user" (
            id SERIAL PRIMARY KEY,
            email VARCHAR(254) UNIQUE NOT NULL,
            password TEXT NOT NULL
        );
    """)

    conn.commit()
    cur.close()
    conn.close()