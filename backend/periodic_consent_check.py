from time import sleep
from redis_connection import r
import asyncio
import time
import json
from security import get_hashed_id
#import logging

#logger = logging.getLogger('uvicorn.error')
#logger.setLevel(logging.DEBUG)

# Da controllare se i dati esistono già nel database prima di mandare il fetch
# Da controllare se c'è qualche /revoke prima e /consent dopo relativa allo stesso server
# Da controllare se c'è qualche /revoke all e poi subito dopo /consent (e quel consent specifico se sta nel database), così da eliminare solo gli altri, non tutti
async def check_scheduled():
    while True:
        try:
            print("Entering check_scheduled()")
            now = time.time()
            tasks_to_fetch = r.zrangebyscore("scheduled_fetches", 0, now, withscores=True)
            tasks_to_delete = r.zrangebyscore("scheduled_deletes", 0, now, withscores=True)

            pipe = r.pipeline()
            pipe.zremrangebyscore("scheduled_fetches", 0, now)
            pipe.zremrangebyscore("scheduled_deletes", 0, now)
            pipe.execute()


            to_adjust_fetches = []
            to_adjust_deletes = []

            for task_json, score in tasks_to_fetch:
                task = json.loads(task_json)
                task['timestamp'] = score 
                to_adjust_fetches.append(task)

            for task_json, score in tasks_to_delete:
                task = json.loads(task_json)
                task['timestamp'] = score
                to_adjust_deletes.append(task)

            fetches, deletes = await adjust_tasks(tasks_to_fetch=to_adjust_fetches, tasks_to_delete=to_adjust_deletes)
            # chiamate a bot per fetches
            # chiamata a db per deletes
        except Exception as e:
            print(f"Error in task runner: {e}")

        await asyncio.sleep(30)

# ricorda, i fetch hanno id in chiaro, i delete hashati
async def adjust_tasks(tasks_to_fetch: list, tasks_to_delete: list):
    adjusted_fetches = []
    adjusted_deletes = []

    db_servers = []
    # avrò una lista ordinata temporalmente di "tasks_to_fetch" aka consent e "tasks_to_delete" aka revoke
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

    # ora controlla se su redis c'è qualche /consent corrispondente incoming
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

    

    for fetch_t in tasks_to_fetch:
        u_h = get_hashed_id(fetch_t['u'])
        s_h = get_hashed_id(fetch_t['s'])

        # Se l'utente è già nel Database per questo server, il fetch è inutile
        # Usiamo una chiamata al backend
        already_exists = [] # await check_if_user_exists_in_db(u_h, s_h)
        
        if not already_exists:
            adjusted_fetches.append(fetch_t)
    
    # Ritorna le liste aggiustate
    return adjusted_fetches, adjusted_deletes
    