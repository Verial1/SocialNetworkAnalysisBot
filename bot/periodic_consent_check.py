from redis_connection import r
import asyncio
import time
import json
from periodic_utils import adjust_fetches, adjust_deletes, check_future_consents_redis

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
            print("tasks_to_fetch: " + str(tasks_to_fetch))
            print("tasks_to_delete: " + str(tasks_to_delete))
            fetches, deletes = await adjust_tasks(tasks_to_fetch=to_adjust_fetches, tasks_to_delete=to_adjust_deletes)
            print("After adjustment:")
            print("fetches: " + str(fetches))
            print("deletes: " + str(deletes))
            # chiamate a bot per fetches
            # chiamata a db per deletes
        except Exception as e:
            print(f"Error in task runner: {e}")

        await asyncio.sleep(30)

# ricorda, i fetch hanno id in chiaro, i delete hashati
async def adjust_tasks(tasks_to_fetch: list, tasks_to_delete: list):
    d_list = await adjust_deletes(tasks_to_fetch=tasks_to_fetch, tasks_to_delete=tasks_to_delete)
    d_list = await check_future_consents_redis(adjusted_deletes=d_list)
    f_list = await adjust_fetches(tasks_to_fetch=tasks_to_fetch)
    
    # Ritorna le liste aggiustate
    return f_list, d_list
