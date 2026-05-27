from bot.core.redis_connection import r
from bot.core.security import get_hashed_id
import json
import time

async def schedule_gap_fills(session_start_id: int):
    user_keys = r.keys("active_consents:*") 
    
    for key in user_keys:
        user_id = key.split(":")[1] # Estrae l'ID in chiaro, usare scan???
        servers = r.smembers(key) 
        
        for server_id in servers:
            u_hash = get_hashed_id(user_id)
            s_hash = get_hashed_id(server_id)
            # Chiediamo al backend dove eravamo rimasti (usando gli hash)
            last_id = 1 #await backend_api.get_latest_id(u_hash, s_hash)
            
            if last_id:
                # Programmiamo il compito di riparazione
                task = json.dumps({
                    "u": user_id, "s": server_id, 
                    "type": "gap_fill", 
                    "min_id": last_id, 
                    "stop_id": session_start_id
                })
                r.zadd("scheduled_fetches", {task: time.time() + 10})