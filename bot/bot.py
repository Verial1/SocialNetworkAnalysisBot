import discord
from dotenv import load_dotenv
import os
import httpx
import asyncio
from clean import clean_message
import random

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DISCORD_URL = os.getenv("DISCORD_URL")

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    print(str(DISCORD_URL))
    await message_history(guild_id=str(724405288731541526), author_id=str(1247659397916917861), limit=25, min_id=str(1247666743070036048))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

# min_id optional, as such, if a user is just added with no saved messages (Null in the DB), we can start getting messages from oldest to latest
# if len(batch) is empty, finished messages (up to date)
# i get rate limited, why?
async def message_history(guild_id: str, author_id: str, min_id: str = "-1", limit: int = 25):
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
            await asyncio.sleep(random.uniform(0.6, 1.0)) 
            response = await http_client.get(url, headers=headers, params=params)

            if response.status_code == 429:
                data = response.json()
                wait_time = data.get("retry_after", 5)  + random.uniform(0.3, 0.6)
                is_global = data.get("global", False)
                
                print(f"Rate Limit {'GLOBAL' if is_global else 'Path'}. Wait: {wait_time}s")
                await asyncio.sleep(wait_time)
                continue

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

            
            elif response.status_code == 202:
                if retries_202 < max_retries_202:
                    wait_time = response.json().get("retry_after", 5) + random.uniform(0.3, 0.6)
                    print(f"Discord is indexing... Wait: {wait_time}s")
                    await asyncio.sleep(wait_time)
                    retries_202 += 1
                    continue
                else:
                    print("Timeout Discord indexing.")
                    break

            else:
                print("Error: " + str(response.status_code) + " - " + response.text)
                return []
            
            remaining = response.headers.get("X-RateLimit-Remaining")
            if remaining == "0":
                reset_after = float(response.headers.get("X-RateLimit-Reset-After", 1)) + random.uniform(0.3, 0.6)
                print(f"Bucket finished. Pausing {reset_after}s")
                await asyncio.sleep(reset_after)
    print(all_messages)
    return all_messages


client.run(str(DISCORD_TOKEN))
