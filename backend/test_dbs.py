#On one terminal run uvicorn bots.profile_bot:app --host 0.0.0.0 --port 8000
#On another terminal run curl -X POST http://127.0.0.1:8000/profile/summarize -H "Content-Type: application/json" -d "{\"user_id\": 1, \"paragraph\": \"I'm an investor who loves coding and is good at video editing. I also enjoy startups and tech projects.\"}"

'''
Run: python test_dbs.py.
Confirmation: Prints "PG Connected Successfully!" and "VectorDB Collection: user_vectors". If errors:
PG: Check creds/IP (ensure CVM IP allowed in TencentDB security group).
VectorDB: Wrong endpoint/key? Check logs; if collection creation fails, verify dimension/model in .env (BGE_BASE_ZH is 768-dim).
Fix: Tencent Console > VectorDB > Logs for details.
'''

from utils.db_utils import get_pg_connection, get_vdb_collection
from utils.db_utils import embed_text, query_vector_db, get_user_infos

try: 
    vec=embed_text("test")
    ids=query_vector_db(vec, 5)
    print(ids)
    infos=get_user_infos(ids)
    print(infos)
except Exception as e:
    print("Error in vector DB operations:", e)


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