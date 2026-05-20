import discord
from dotenv import load_dotenv
import os
from get_data import get_message_history, get_self, get_self_servers, get_user_data, get_server_data
from manage_consent import user_consent, revoke_user_consent, revoke_user_consent_all
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
    #await get_message_history(guild_id=str(724405288731541526), author_id=str(461637314276360204), limit=25, min_id=str(848592092623929375), debug=True)
    #await get_user_data(user_id=str(461637314276360204), guild_id=str(724405288731541526))
    #await get_server_data(guild_id=str(724405288731541526))

    # do i care?
    # gets server list from DB
    # calls get_self_servers()
    # compare
    # if compare results in a discrepancy
    #   unregistered servers -> a



@client.event
async def on_message(message):
    
    if message.author == client.user:
        return

    if message.content.startswith('/consent'):
        res = user_consent(user_id=str(message.author.id), guild_id=str(message.guild.id))
        if res:                                                                                     # remember to change to ping user
            await message.channel.send('Consent to get ' + str(message.author.name) + '\'s messages granted succesfully.')
        else:
            await message.channel.send('Consent already given by: ' + str(message.author.name))

    if "/revoke" in message.content and "/revokeall" not in message.content:
        pattern = r'^/revoke\s+(\d{17,19})'
        match = re.search(pattern, message.content)

        if match:
            guild_id = str(match.group(1))
        else:
            guild_id = str(message.guild.id)
    
        res = revoke_user_consent(user_id=str(message.author.id), guild_id=str(guild_id))
        if res:
            await message.channel.send('Succefully revoked ' + str(message.author.name) + '\'s consent in: ' + str(guild_id))
        else:
            await message.channel.send('No consent has been given in this guild in the past.')

    if "/revokeall" in message.content:
        res = revoke_user_consent_all(user_id=str(message.author.id))
        if res:
            await message.channel.send('Succefully revoked ' + str(message.author.name) + '\'s consent from all servers.')
        else:
            await message.channel.send('No consent has been given in any guild in the past.')

client.run(str(DISCORD_TOKEN))
