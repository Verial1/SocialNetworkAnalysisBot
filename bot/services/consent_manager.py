import json
import time
import redis
from bot.core.security import get_hashed_id
from bot.core.redis_connection import r

GRACE_PERIOD = 10 # put 300 to default

def add_consent(user_id: str, server_id: str):
    u_hash = get_hashed_id(user_id)
    s_hash = get_hashed_id(server_id)
    try:
        pipe = r.pipeline()

        pipe.sadd(f"active_consents:{user_id}", server_id)

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
            pipe.delete(f"active_consents:{user_id}")
        else:
            pipe.srem(f"active_consents:{user_id}", server_id)
            fetch_task = json.dumps({"u": user_id, "s": server_id})
            pipe.zrem("scheduled_fetches", fetch_task)
        
        if immediate:
            # bot dovrà fare chiamata al backend per Postgres, oppure mtogliergli il grace_period? # await delete_user_data(u_hash, s_hash)
            pass 
        else:
            process_at = time.time() + GRACE_PERIOD
            if server_id == "all":
                delete_task = json.dumps({"u": u_hash, "s": "all"})
            else:
                delete_task = json.dumps({"u": u_hash, "s": u_hash})
            pipe.zadd("scheduled_deletes", {delete_task: process_at})

        pipe.execute()
        return True
    except redis.RedisError as e:
        print(f"Redis Error in add_revoke: {e}")
        return False
    except Exception as e:
        print(f"Error in add_revoke: {e}")
        return False