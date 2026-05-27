import httpx
import asyncio
from datetime import datetime
from dotenv import load_dotenv
from utils.formatters import clean_message, clean_self_server, clean_user, clean_guild
from bot.core.redis_connection import r
import os

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DISCORD_URL = os.getenv("DISCORD_URL")

MAX_RETRIES_202 = 5

# --- BOT ---
# Gets bot's id (is it useful lol?)
async def get_self():
    self_id = None
    retries_202 = 0
    
    url = str(DISCORD_URL) + "/users/@me"
    headers = {
        "Authorization": "Bot " + str(DISCORD_TOKEN)
    }
    params = {}

    async with httpx.AsyncClient() as http_client:
        while True:
            response = await http_client.get(url, headers=headers, params=params)

            if response.status_code == 429:
                data = response.json()
                wait_time = data.get("retry_after", 5)
                await asyncio.sleep(wait_time)
                continue

            elif response.status_code == 202:
                if retries_202 < MAX_RETRIES_202:
                    data = response.json()
                    wait_time = data.get("retry_after", 5)
                    print(f"Discord is indexing... Wait: {wait_time}s")
                    await asyncio.sleep(wait_time)
                    retries_202 += 1
                    continue
                else:
                    print("Timeout Discord indexing.")
                    break

            elif response.status_code == 200:
                self_id = response.json().get("id")
                break

            else:
                print("Error: " + str(response.status_code) + " - " + response.text)
                break
    return self_id

# Gets bot's server/guild ids
async def get_self_servers():
    servers = []
    retries_202 = 0

    url = str(DISCORD_URL) + "/users/@me/guilds"
    headers = {
        "Authorization": "Bot " + str(DISCORD_TOKEN)
    }
    params = {}

    async with httpx.AsyncClient() as http_client:
        while True:
            response = await http_client.get(url, headers=headers, params=params)

            if response.status_code == 429:
                data = response.json()
                wait_time = data.get("retry_after", 5)
                await asyncio.sleep(wait_time)
                continue

            elif response.status_code == 202:
                if retries_202 < MAX_RETRIES_202:
                    data = response.json()
                    wait_time = data.get("retry_after", 5)
                    print(f"Discord is indexing... Wait: {wait_time}s")
                    await asyncio.sleep(wait_time)
                    retries_202 += 1
                    continue
                else:
                    print("Timeout Discord indexing.")
                    break

            elif response.status_code == 200:
                batch = response.json()
                for elem in batch:
                    cleaned = clean_self_server(elem)
                    servers.append(cleaned)
                break

            else:
                print("Error: " + str(response.status_code) + " - " + response.text)
                break
    
    return servers

# --- USER ---
# Gets user's data in a specified server
async def get_user_data(user_id: str, guild_id: str):
    user_data = None
    retries_202 = 0
    
    url = str(DISCORD_URL) + "/guilds/" + str(guild_id) + "/members/" + str(user_id)
    headers = {
        "Authorization": "Bot " + str(DISCORD_TOKEN)
    }
    params = {}
    
    async with httpx.AsyncClient() as http_client:
        while True:
            response = await http_client.get(url, headers=headers, params=params)

            if response.status_code == 429:
                data = response.json()
                wait_time = data.get("retry_after", 5)
                await asyncio.sleep(wait_time)
                continue

            elif response.status_code == 202:
                if retries_202 < MAX_RETRIES_202:
                    data = response.json>()
                    wait_time = data.get("retry_after", 5)
                    print(f"Discord is indexing... Wait: {wait_time}s")
                    await asyncio.sleep(wait_time)
                    retries_202 += 1
                    continue
                else:
                    print("Timeout Discord indexing.")
                    break

            elif response.status_code == 200:
                data = response.json()
                user_data = clean_user(data)
                print(user_data)
                break

            else:
                print("Error: " + str(response.status_code) + " - " + response.text)
                break
    return user_data

# --- SERVER/GUILD ---
# Gets server's data
async def get_server_data(guild_id: str):
    server_data = None
    retries_202 = 0
    
    url = str(DISCORD_URL) + "/guilds/" + str(guild_id)
    headers = {
        "Authorization": "Bot " + str(DISCORD_TOKEN)
    }
    params = {}

    async with httpx.AsyncClient() as http_client:
        while True:
            response = await http_client.get(url, headers=headers, params=params)

            if response.status_code == 429:
                data = response.json()
                wait_time = data.get("retry_after", 5)
                await asyncio.sleep(wait_time)
                continue

            elif response.status_code == 202:
                if retries_202 < MAX_RETRIES_202:
                    data = response.json>()
                    wait_time = data.get("retry_after", 5)
                    print(f"Discord is indexing... Wait: {wait_time}s")
                    await asyncio.sleep(wait_time)
                    retries_202 += 1
                    continue
                else:
                    print("Timeout Discord indexing.")
                    break

            elif response.status_code == 200:
                data = response.json()
                server_data = clean_guild(data)
                break

            else:
                print("Error: " + str(response.status_code) + " - " + response.text)
                break
    return server_data

# --- MESSAGE HISTORY ---
# min_id optional, as such, if a user has just been added with no saved messages (Null in the DB), we can start getting messages from oldest to latest
# if len(batch) is empty, finished messages (up to date)
# i get rate limited, why?
# da fare con i semafori/mutex/lock? Che forse creo più task e devo rispettare i limiti di discord in maniera condivisaS
# da aggiungere un wait in caso di /revoke così che si da spazio alle altre requests? e se il revoke va in porto si killa ufficialmente, se no se c'è un consent può riprendere
async def get_message_history(guild_id: str, author_id: str, message_id: str = "-1", limit: int = 25, order: str = "asc", stop_id = None, debug: bool = False,):
    all_messages = []
    retries_202 = 0
    current_id = message_id

    url = str(DISCORD_URL) + "/guilds/" + guild_id + "/messages/search"
    headers = {
        "Authorization": "Bot " + str(DISCORD_TOKEN)
    }
    params = {
        "author_id": author_id,
        "limit": limit,
    }
    if(message_id != "-1"):
        if order == "asc":
            params["min_id"] = current_id
            if stop_id:
                params["max_id"] = stop_id    
        else:
            params["max_id"] = current_id

    async with httpx.AsyncClient() as http_client:
        while True:
            # checks if redis consent is still active
            if not r.sismember(f"active_consents:{author_id}", guild_id):
                print("Fetch interrupted: consent revoked.")
                return [], current_id

            if debug:
                now = datetime.now().strftime("%H:%M:%S:%f")
                print("\nRequest time: " + str(now))

            response = await http_client.get(url, headers=headers, params=params)

            if debug:
                print("Status code: " + str(response.status_code))
                print("Limit: " + str(response.headers.get("X-RateLimit-Limit")))
                print("Remaining: " + str(response.headers.get("X-RateLimit-Remaining")))
                print("Reset-After: " + str(response.headers.get("X-RateLimit-Reset-After")))
                print("Bucket: " + str(response.headers.get("X-RateLimit-Bucket")))
                print("Scope: " + str(response.headers.get("X-RateLimit-Scope")))
                print("retry_after: " + str(response.json().get("retry_after")))
                print("global: " + str(response.json().get("global")))

            if response.status_code == 429:
                data = response.json()
                wait_time = data.get("retry_after", 5) + 0.5
                await asyncio.sleep(wait_time)
                continue

            elif response.status_code == 202:
                if retries_202 < MAX_RETRIES_202:
                    wait_time = response.json().get("retry_after", 5)
                    print(f"Discord is indexing... Wait: {wait_time}s")
                    await asyncio.sleep(wait_time)
                    retries_202 += 1
                    continue
                else:
                    print("Timeout Discord indexing.")
                    break

            elif response.status_code == 200:
                batch = response.json().get("messages", [])
                if(len(batch) == 0):
                    break
                current_id = batch[-1][0]["id"]
                for elem in batch:
                    cleaned = clean_message(elem)
                    all_messages.append(cleaned)
                retries_202 = 0

            else:
                print("Error: " + str(response.status_code) + " - " + response.text)
                return [], current_id
            
            remaining = response.headers.get("X-RateLimit-Remaining")
            if remaining == "0":
                reset_after = float(response.headers.get("X-RateLimit-Reset-After", 5))
                print("Bucket finished. Pausing " + str(reset_after) + "s")
                await asyncio.sleep(reset_after)
    
    return all_messages, message_id