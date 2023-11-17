import discord
from discord.ext import commands
from discord.ext import tasks
import requests
import json
from datetime import datetime, timedelta

intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix='>', intents=intents)

with open('config.json', 'r') as cfg:
    config = json.loads(cfg.read())

pick=0

@tasks.loop(seconds=60)
async def newloop():
    try:
        response = requests.get(config["HostUrl"])
        print (f"Server response: {response.text}")

        for object in json.loads(response.text):
            if object["name"] == config["ServerName"]:
                responseObject = object

        online = int(responseObject["online"])
        maxPlayers = int(responseObject["maxPlayers"])

        print (f"Players online: {online}/{maxPlayers}")

        for channelId in config["ChannelIds"]:
            try:
                await (client.get_channel(channelId)).send(f":busts_in_silhouette: Игроков онлайн: {online}/{maxPlayers}", delete_after=60)
            except Exception as ex:
                print(f"Failed to send message into: {channelId}. Reason {ex}")


        global pick
        if online >= pick:
            pick = online
        
        now = datetime.now()
        target = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        global diff
        diff = (target - now).total_seconds()
        diff = int(diff)
        date = str(now)
        date = date.partition(' ')[0]
        print (f"Пиковый oнлайн за день({date}): {pick}")

        if diff <= 60 :
            for channelId in config["ChannelIds"]:
                try:
                    await client.get_channel(channelId).send(f":bar_chart: Пиковый онлайн ({date}): {pick}") 
                except Exception as ex:
                    print(f"Failed to send message into: {channelId}. Reason {ex}")
            pick = 0
    except Exception as ex:
        print(f"Something went wrong! Reason: {ex}")

@newloop.before_loop
async def before_newloop():
  await client.wait_until_ready()

@client.event
async def on_ready():
    newloop.start()

client.run(config["BotToken"])