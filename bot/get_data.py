import httpx
import asyncio
from datetime import datetime
from dotenv import load_dotenv
from clean import clean_message
import os

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DISCORD_URL = os.getenv("DISCORD_URL")

async def get_servers():
    j = 1
    # to define

async def get_user(user_id: str):
    url = str(DISCORD_URL) + "/users/" + "@" + user_id + "/guilds"
    j = 1
    # to define


# min_id optional, as such, if a user is just added with no saved messages (Null in the DB), we can start getting messages from oldest to latest
# if len(batch) is empty, finished messages (up to date)
# i get rate limited, why?
async def get_message_history(guild_id: str, author_id: str, min_id: str = "-1", limit: int = 25, debug: bool = False):
    all_messages = []
    retries_202 = 0
    max_retries_202 = 5

    url = str(DISCORD_URL) + "/guilds/" + guild_id + "/messages/search"
    headers = {
        "Authorization": "Bot " + str(DISCORD_TOKEN)
    }
    params = {
        "author_id": author_id,
        "limit": limit,
        "sort_order": "asc",
    }
    if(min_id != "-1"):
        params["min_id"] = min_id

    async with httpx.AsyncClient() as http_client:
        while True:
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
                wait_time = data.get("retry_after", 5)
                await asyncio.sleep(wait_time)
                continue

            elif response.status_code == 202:
                if retries_202 < max_retries_202:
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
                min_id = batch[-1][0]["id"]
                for elem in batch:
                    cleaned = clean_message(elem)
                    all_messages.append(cleaned)
                params["min_id"] = min_id
                retries_202 = 0

            else:
                print("Error: " + str(response.status_code) + " - " + response.text)
                return []
            
            remaining = response.headers.get("X-RateLimit-Remaining")
            if remaining == "0":
                reset_after = float(response.headers.get("X-RateLimit-Reset-After", 5))
                print("Bucket finished. Pausing " + str(reset_after) + "s")
                await asyncio.sleep(reset_after)
    
    return all_messages