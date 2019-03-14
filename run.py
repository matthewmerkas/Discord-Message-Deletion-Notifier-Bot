import discord
import asyncio
import configparser
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
timezone = int(config['DEFAULT']['timezone'])
output = config['DEFAULT'].getboolean('output')
command_delete = config['DEFAULT'].getboolean('output')
status_delete = int(config['DEFAULT']['status_delete'])

global context_memory
context_memory = None

client = Bot(command_prefix=BOT_PREFIX)
client.remove_command('help')

@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game(name='Notifications ON'))

@client.command()
async def help(context):
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
    if(context_memory == None):
        if(message.author != client.user) and (output):
            await send_notification(message)
    else:
        if(message.author != client.user) and (message != context_memory.message) and (output):
            await send_notification(message)

async def send_notification(message):
    channel = message.channel
    user = message.author.nick
    utc = message.created_at
    hour = (utc.hour + timezone) % 24
    date = "{}-{}-{}".format(utc.day, utc.month, utc.year)
    time = "{}:{}:{}".format(hour, utc.minute, utc.second)
    await channel.send("Someone deleted {}'s message which was sent at {} on {}".format(user, time, date))

client.run(TOKEN)
