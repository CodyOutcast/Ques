from utils.db_utils import get_pg_connection, get_vdb_collection

try:
    conn = get_pg_connection()
    cur = conn.cursor()
    cur.execute("SELECT 1;")
    print("PG Connected Successfully!")
    cur.close()
    conn.close()
except Exception as e:
    print("PG Error:", e)

try:
    coll = get_vdb_collection()
    print("VectorDB Collection:", coll.collection_name)
    # Test a dummy insert if desired
except Exception as e:
    print("VectorDB Error:", e)