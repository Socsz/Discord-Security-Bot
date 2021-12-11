import discord
import platform
from discord.ext import commands, tasks
import os
from asyncio import sleep
import json
from pathlib import Path
from config import TOKEN, PREFIX, OWNER


intents = discord.Intents.all()
intents.members = True



bot = commands.Bot(command_prefix=PREFIX, intents=intents, case_insensitive=True, owner_id=OWNER)
for filename in os.listdir('./cogs'):
    if filename.endswith(".py"):
        bot.load_extension(f'cogs.{filename[:-3]}')


@bot.event
async def on_ready():
    pythonVersion = platform.python_version()
    print(f'We have logged in as {bot.user}')
    print(discord.__version__)
    print(pythonVersion)



@tasks.loop(seconds=10)
async def statusloop():
    await bot.wait_until_ready()
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"{PREFIX}help"))
    await sleep(10)
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"over {len(bot.guilds)} guilds"))
    await sleep(10)
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"over {len(set(bot.get_all_members()))} members"))
    await sleep(10)
statusloop.start()

bot.run(TOKEN)