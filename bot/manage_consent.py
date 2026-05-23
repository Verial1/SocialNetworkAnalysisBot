import json
import time
from security import get_hashed_id
from redis_connection import r
import redis


def add_consent(user_id: str, server_id: str):
    u_hash = get_hashed_id(user_id)
    s_hash = get_hashed_id(server_id)
    try: 
        pipe = r.pipeline()
        
        pipe.sadd(f"active_consents:{u_hash}", s_hash)
        
        process_at = time.time() + 300
        task_data = json.dumps({"u": user_id, "s": server_id})
        pipe.zadd("scheduled_fetches", {task_data: process_at})
        
        pipe.execute()
        return True
    except redis.RedisError as e:
        print(f"Redis Error in add_consent: {e}")
        return False
    except Exception as e:
        print(f"General Error in add_consent: {e}")
        return False

def add_revoke(user_id: str, server_id: str):
    u_hash = get_hashed_id(user_id)
    s_hash = get_hashed_id(server_id)
    try:
        pipe = r.pipeline()

        if server_id == "all":
            pipe.delete(f"active_consents:{u_hash}")
            pipe.lpush("revoke_queue", json.dumps({"u_hash": u_hash, "s_hash": "all"}))
        else:
            # active_consents is useful for tracking messages live
            pipe.srem(f"active_consents:{u_hash}", s_hash)
            # for postgres revoke at midnight
            pipe.lpush("revoke_queue", json.dumps({"u_hash": u_hash, "s_hash": s_hash}))

        pipe.execute()
        return True
    except redis.RedisError as e:
        print(f"Redis Error in add_revoke: {e}")
        return False
    except Exception as e:
        print(f"General Error in add_revoke: {e}")
        return False