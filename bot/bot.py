import discord
from dotenv import load_dotenv
import os
from fetch_data import fetch_message_history

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DISCORD_URL = os.getenv("DISCORD_URL")

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

    await fetch_message_history(guild_id=str(724405288731541526), author_id=str(461637314276360204), limit=25, min_id=str(848592092623929375), debug=True)


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

client.run(str(DISCORD_TOKEN))
