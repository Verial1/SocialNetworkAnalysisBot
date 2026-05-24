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
            # da controllare se si può fare la remove by range piuttosto che singoli oggetti
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


async def adjust_tasks():
    pass
    # avrò una lista ordinata temporalmente di "tasks_to_fetch" aka consent e "tasks_to_delete" aka revoke

    # Controlla se c'è un revokeall poi un consent
    #   SE SI: 
    #       fetcha la lista di servers in cui è l'utente (postgres)
    #       SE nella lista ricevuta c'è anche quella per cui c'è il consent:
    #           elimina dalla lista ricevuta il server per cui c'è il consenso
    #       controlla se su Redis c'è un consent incoming su uno dei server che si sta eliminando (serve perché magari il consent è stato fatto 10 secondi dopo, dopo 5 minuti e 1 secondo dal revoke c'è il fetch da redis e il consent di 9 secondi dopo se no verrebbe ignorato e ci sarebbe un fetch in più che sarebbe potuto essere risparmiato)
    #       SE SI: toglilo dalla lista di quelli da cancellare
    #       usa tale lista per defininire gli argomenti della chiamata wipe_user_data o quel che è

    # Controlla se il consent è stato già dato (fetcha la lista di servers in cui è l'utente, magari fallo ad inizio funzione che è utile pure per il revokeall)
    #   SE SI: eliminalo dalla lista dei consent, inutile riprendere i dati
    
    # Ritorna le liste aggiustate
    