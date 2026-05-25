from security import get_hashed_id
import json
from redis_connection import r

async def adjust_deletes(tasks_to_fetch: list, tasks_to_delete: list):
    adjusted_deletes = []

    for delete_t in tasks_to_delete:
        # se /revokeall
        if delete_t['s'] == "all":
            db_servers = [] # await get_servers_from_db(d_task['u'])    # Recupera i server dal DB Postgres
            
            # Controllo la lista dei fetch
            for fetch_t in tasks_to_fetch:
                # converto in hash per avere i corrisponendi dei delete (che sono già hashati)
                fetch_t_u_hashed = get_hashed_id(fetch_t['u']) 
                fetch_t_s_hashed = get_hashed_id(fetch_t['s']) 
                # se user_id del fetch e delete corrispondono, e il timestamp di tale fetch è più recente del revokeall
                if fetch_t_u_hashed == delete_t['u'] and fetch_t['timestamp'] > delete_t['timestamp']:
                    # cancellalo dai revoke
                    if fetch_t_s_hashed in db_servers:
                        db_servers.remove(fetch_t_s_hashed)
            
            # aggiungi i server risultanti alla lista pulita
            for s in db_servers:
                adjusted_deletes.append({
                    "u": delete_t['u'],
                    "s": s,
                    "timestamp": delete_t['timestamp']
                })
        else:
            adjusted_deletes.append(delete_t)

    return adjusted_deletes

async def check_future_consents_redis(adjusted_deletes: list):
    future_fetches = r.zrange("scheduled_fetches", 0, -1)
    future_consents = set()
    for future_task_json in future_fetches:
                ft = json.loads(future_task_json)
                u_h = get_hashed_id(ft['u'])
                s_h = get_hashed_id(ft['s'])
                future_consents.add((u_h, s_h))

    adjusted_deletes = [
            d for d in adjusted_deletes 
            if (d['u'], d['s']) not in future_consents
        ]
    
    return adjusted_deletes

async def adjust_fetches(tasks_to_fetch: list):
    adjusted_fetches = []
    
    for fetch_t in tasks_to_fetch:
        u_h = get_hashed_id(fetch_t['u'])
        s_h = get_hashed_id(fetch_t['s'])

        # Se l'utente è già nel Database per questo server, il fetch è inutile
        # Usiamo una chiamata al backend
        already_exists = [] # await check_if_user_exists_in_db(u_h, s_h)
        
        if not already_exists:
            adjusted_fetches.append(fetch_t)
    
    return adjusted_fetches