import discord
from dotenv import load_dotenv
import os
from get_data import get_message_history, get_self, get_self_servers, get_user_data, get_server_data
from manage_consent import add_consent, add_revoke
import re

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DISCORD_URL = os.getenv("DISCORD_URL")

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')


# DA AGGIUNGERE 'now' come keyword per forzare il delete istantaneo?
@client.event
async def on_message(message):
    
    if message.author == client.user:
        return

    if message.content.startswith('/consent'):
        res = add_consent(user_id=str(message.author.id), server_id=str(message.guild.id))
        if res:                                                                                     # remember to change to ping user
            await message.reply('Consent to get ' + message.author.mention + '\'s messages granted succesfully.')
        else:
            await message.reply('Error in giving consent. Please retry.')

    if "/revoke" in message.content and "/revokeall" not in message.content and message.content.startswith('/revoke'):
        pattern = r'^/revoke\s+(\d{17,19})'
        match = re.search(pattern, message.content)

        if match:
            guild_id = str(match.group(1))
        else:
            guild_id = str(message.guild.id)
    
        res = add_revoke(user_id=str(message.author.id), server_id=str(guild_id))
        if res:
            await message.reply('Succefully revoked ' + message.author.mention + '\'s consent in: ' + str(guild_id))
        else:
            await message.reply('Error in revoking consent. Please retry.')

    if "/revokeall" in message.content and message.content.startswith('/revokeall'):
        res = add_revoke(user_id=str(message.author.id), server_id="all")
        if res:
            await message.reply('Succefully revoked ' + message.author.mention + '\'s consent from all servers.')
        else:
            await message.reply('Error in revoking consent. Please retry.')

client.run(str(DISCORD_TOKEN))
