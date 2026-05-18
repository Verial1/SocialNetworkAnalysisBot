import discord
from dotenv import load_dotenv
import os
import httpx
import asyncio
#from clean import clean_message

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
    await message_history(guild_id=str(1505603927369060582), author_id=str(461637314276360204), limit=5, min_id=str(1505972118012166214))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

# min_id optional, as such, if a user is just added with no saved messages (Null in the DB), we can start getting messages from oldest to latest
# if len(batch) is empty, finished messages (up to date)
async def message_history(guild_id: str, author_id: str, min_id: str = "-1", limit: int = 25):
    all_messages = []

    retries_202 = 0
    max_retries_202 = 5

    url = str(DISCORD_URL) + "/guilds/" + guild_id + "/messages/search"
    headers = {
        "Authorization": "Bot " + str(DISCORD_TOKEN)
    }
    if min_id == "-1":
        params = {
            "author_id": author_id,
            "limit": limit,
            "sort_order": "asc",
        }
    else:
        params = {
            "author_id": author_id,
            "limit": limit,
            "sort_order": "asc",
            "min_id": min_id
        }

    async with httpx.AsyncClient() as client:
        #while True:
        response = await client.get(url, headers=headers, params=params)
        if response.status_code == 200:
            batch = response.json().get("messages", [])
            if(len(batch) == 0):
                return []
            
            print(str(response.json()))
            
            min_id = batch[-1][0]["id"]

            for elem in batch:
                elem = clean_message(elem)
                all_messages.append(elem)

            params["min_id"] = min_id

            retries_202 = 0
        
        elif response.status_code == 202:
            if retries_202 < max_retries_202:
                wait_time = response.json().get("retry_after", 5)
                await asyncio.sleep(wait_time)
                retries_202 += 1
            else:
                print("Timeout indexing Discord.")

        # 204 requested completed but no content return, da fare?

        elif response.status_code == 429: # Rate Limit
            wait_time = response.json().get("retry_after", 10)
            await asyncio.sleep(wait_time)

        else:
            print("Error: " + str(response.status_code) + " - " + response.text)
            return []
    
    print("Return message")
    return all_messages


client.run(str(DISCORD_TOKEN))
