import psycopg2
import os

def get_conn():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "postgres"),
        dbname=os.getenv("DB_NAME", "supply_chain_db"),
        user=os.getenv("DB_USER", "supply_chain_user"),
        password=os.getenv("DB_PASS", "supply_chain_pass"),
        port=int(os.getenv("DB_PORT", 5432)),
    )