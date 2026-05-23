import json
import time
from security import get_hashed_id
from redis_connection import r


def add_consent(user_id: str, server_id: str):
    u_hash = get_hashed_id(user_id)
    s_hash = get_hashed_id(server_id)

    r.sadd(f"active_consents:{u_hash}", s_hash)
    
    # ZSET
    process_at = time.time() + 300 # process at 5 minutes from now
    task_data = json.dumps({"u": user_id, "s": server_id})
    r.zadd("scheduled_fetches", {task_data: process_at})

def add_revoke(user_id: str, server_id: str = "all"):
    u_hash = get_hashed_id(user_id)
    s_hash = get_hashed_id(server_id)

    if server_id == "all":
        r.delete(f"active_consents:{u_hash}")

        r.lpush("revoke_queue", json.dumps({"u": u_hash, "s": "all"}))
        
    else:
        # active_consents is useful for tracking messages live
        r.srem(f"active_consents:{u_hash}", s_hash)

        # for postgres revoke at midnight
        r.lpush("revoke_queue", json.dumps({"u": u_hash, "s": s_hash}))
