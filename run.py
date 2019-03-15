import discord
import asyncio
import configparser
from datetime import timedelta
from datetime import time
from datetime import date
from pytz import timezone
from tzlocal import get_localzone
from discord.ext.commands import Bot

"""
Discord bot that announces when a message is deleted (including who posted it and when).
Discord doesn't allow viewing who deleted a message, but this feature can be added later if it becomes possible
Only notifies for messages in the bot's message cache, which defaults to 5000 messages,
and only for messages posted while the bot is online
"""

config = configparser.ConfigParser(interpolation=None)
config.read('config.ini')
TOKEN = config['DEFAULT']['TOKEN']
BOT_PREFIX = config['DEFAULT']['BOT_PREFIX']
loc_tz = int(config['DEFAULT']['timezone'])
output = config['DEFAULT'].getboolean('output')
command_delete = config['DEFAULT'].getboolean('output')
status_delete = int(config['DEFAULT']['status_delete'])
notification_message = ":warning: " + config['DEFAULT']['notification_message']

context_memory = None

client = Bot(command_prefix=BOT_PREFIX)
client.remove_command('help')

@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game(name='Notifications ON'))

@client.command()
async def help(context):
    global context_memory
    context_memory = context
    embed = discord.Embed(colour = discord.Colour.red())
    embed.set_author(name='Help')
    embed.add_field(name='on', value='Turn the message deletion notifications ON')
    embed.add_field(name='off', value='Turn the message deletion notifications OFF')
    await context.send(embed=embed)
    if(command_delete):
        await context.message.delete()

@client.command()
async def on(context):
    global context_memory
    context_memory = context
    global output
    output = True
    message = await context.send("Message deletion notifications ON")
    await client.change_presence(activity=discord.Game(name='Notifications ON'))
    if(command_delete):
        await context.message.delete()
    if(status_delete > 0):
        await asyncio.sleep(status_delete)
        await message.delete()

@client.command()
async def off(context):
    global context_memory
    context_memory = context
    global output
    output = False
    message = await context.send("Message deletion notifications OFF")
    await client.change_presence(activity=discord.Game(name='Notifications OFF'))
    if(command_delete):
        await context.message.delete()
    if(status_delete > 0):
        await asyncio.sleep(status_delete)
        await message.delete()

@client.event
async def on_message_delete(message):
    #Check if someone's trying to delete a user's message and send a notification
    if(context_memory == None):
        if(message.author != client.user) and (output):
            await send_notification(message)
    else:
        if(message.author != client.user) and (message != context_memory.message) and (output):
            await send_notification(message)
    #Check if someone's trying to delete a notification and repost it
    if(message.author == client.user) and (message.content[:10] == ":warning: "):
        await message.channel.send(message.content)

async def send_notification(message):
    user = message.author.display_name
    #Timezone stuff
    utc_dt = message.created_at
    loc_dt = utc_dt + timedelta(hours=loc_tz)
    dt = date(day=loc_dt.day, month=loc_dt.month, year=loc_dt.year).strftime("%d-%m-%y")
    tm = time(hour=loc_dt.hour, minute=loc_dt.minute, second=loc_dt.second)

    await message.channel.send(notification_message.format(user=user, time=tm, date=dt))

client.run(TOKEN)
