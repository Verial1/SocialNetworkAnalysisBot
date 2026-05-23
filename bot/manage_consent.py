import json
import time
import redis
from security import get_hashed_id
from redis_connection import r

GRACE_PERIOD = 300 

def add_consent(user_id: str, server_id: str):
    u_hash = get_hashed_id(user_id)
    s_hash = get_hashed_id(server_id)
    try:
        pipe = r.pipeline()

        pipe.sadd(f"active_consents:{u_hash}", s_hash)

        delete_task = json.dumps({"u": u_hash, "s": s_hash})
        pipe.zrem("scheduled_deletes", delete_task)
        
        process_at = time.time() + GRACE_PERIOD
        fetch_task = json.dumps({"u": user_id, "s": server_id})
        pipe.zadd("scheduled_fetches", {fetch_task: process_at})
        
        pipe.execute()
        return True
    except redis.RedisError as e:
        print(f"Redis Error in add_revoke: {e}")
        return False
    except Exception as e:
        print(f"Error in add_consent: {e}")
        return False

def add_revoke(user_id: str, server_id: str, immediate: bool = False):
    u_hash = get_hashed_id(user_id)
    s_hash = get_hashed_id(server_id)
    try:
        pipe = r.pipeline()
        
        if server_id == "all":
            pipe.delete(f"active_consents:{u_hash}")
        else:
            pipe.srem(f"active_consents:{u_hash}", s_hash)
        
        if immediate:
            # bot dovrà fare chiamata al backend per Postgres
            pass 
        else:
            process_at = time.time() + GRACE_PERIOD
            delete_task = json.dumps({"u": u_hash, "s": s_hash})
            pipe.zadd("scheduled_deletes", {delete_task: process_at})

        pipe.execute()
        return True
    except redis.RedisError as e:
        print(f"Redis Error in add_revoke: {e}")
        return False
    except Exception as e:
        print(f"Error in add_revoke: {e}")
        return False