from time import sleep
from redis_connection import r
import asyncio
import time
import json

# Da controllare se i dati esistono già nel database prima di mandare il fetch
# Da controllare se c'è qualche /revoke prima e /consent dopo relativa allo stesso server
# Da controllare se c'è qualche /revoke all e poi subito dopo /consent (e quel consent specifico se sta nel database), così da eliminare solo gli altri, non tutti
async def check_scheduled():
    while True:
        try:
            now = time.time()
            tasks_to_fetch = r.zrangebyscore("scheduled_fetches", 0, now)
            tasks_to_delete = r.zrangebyscore("scheduled_deletes", 0, now)

            pipe = r.pipeline()
            for task_json in tasks_to_fetch:
                pipe.zrem("scheduled_fetches", task_json)

            for task_json in tasks_to_delete:            
                pipe.zrem("scheduled_deletes", task_json)
            pipe.execute()

            for task_json in tasks_to_fetch:
                task = json.loads(task_json)
                # anche se mi sa che lo lancerò sul bot non qui nel backend, voglio mantenere i due separati e il bot si interfaccia con i messaggi
                # asyncio.create_task(get_message_history(task['s'], task['u']))

            for task_json in tasks_to_delete:
                task = json.loads(task_json)
                # anche se mi sa che lo lancerò sul bot non qui nel backend, voglio mantenere i due separati e il bot si interfaccia con i messaggi
                # asyncio.create_task(wipe_user_data(task['u'], task['s']))

        except Exception as e:
            print(f"Error in task runner: {e}")

        await asyncio.sleep(30)