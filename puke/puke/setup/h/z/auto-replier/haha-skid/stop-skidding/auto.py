import discord
import os
import secrets
import string
import asyncio
from asyncio import sleep
import json
import random
import pymongo
from pymongo import MongoClient
from discord.ext import commands

cluster = MongoClient('mongodb+srv://blade:A1LnT549zF0XChE0@selfbotdb.qgte1jy.mongodb.net/?retryWrites=true&w=majority')
db = cluster["selfbot_bing"]
collection = db["ego"]
blacklist = db["blacklist"]

intents = discord.Intents.all()
client = commands.Bot(command_prefix='-', help_command = None, self_bot=True, intents=intents)

@client.event
async def on_ready():
    print(" ")
    print("  ██████ ▓█████  ██▓      █████▒    ▄▄▄▄    ▒█████  ▄▄▄█████▓")
    print("▒██    ▒ ▓█   ▀ ▓██▒    ▓██   ▒    ▓█████▄ ▒██▒  ██▒▓  ██▒ ▓▒")
    print("░ ▓██▄   ▒███   ▒██░    ▒████ ░    ▒██▒ ▄██▒██░  ██▒▒ ▓██░ ▒░")
    print("  ▒   ██▒▒▓█  ▄ ▒██░    ░▓█▒  ░    ▒██░█▀  ▒██   ██░░ ▓██▓ ░ ")
    print("▒██████▒▒░▒████▒░██████▒░▒█░       ░▓█  ▀█▓░ ████▓▒░  ▒██▒ ░    via Blade")
    print("▒ ▒▓▒ ▒ ░░░ ▒░ ░░ ▒░▓  ░ ▒ ░       ░▒▓███▀▒░ ▒░▒░▒░   ▒ ░░   ")
    print("░ ░▒  ░ ░ ░ ░  ░░ ░ ▒  ░ ░         ▒░▒   ░   ░ ▒ ▒░     ░    ")
    print("░  ░  ░     ░     ░ ░    ░ ░        ░    ░ ░ ░ ░ ▒    ░      ")
    print("      ░     ░  ░    ░  ░            ░          ░ ░           ")
    print("                                         ░                   ")
    print(' ')
    print(f'[ USER ] {client.user.name} | {client.user.id}')
    print(f'[ GUILDS ] {len(client.guilds)} guilds')
    print(f'[ USERS ] {len(client.users)} users')
    print(f'[ FRIENDS ] {len(client.user.friends)} friends')
    print(' ')

@client.command()
async def ego(ctx, id: int, *, message: str):
    if not collection.find_one({"_id": id}):
        egoed = {"_id": id, "message": message}
        collection.insert_one(egoed)

        message = await ctx.send(f'reaction to {id}, with {message}')
        await sleep(3)
        await message.delete()

    else:
        message = await ctx.send('already exists')
        await sleep(1)
        await message.delete()

@client.command()
async def clearego(ctx, id: int):
    collection.delete_one({"_id": id})
    message = await ctx.send(f'deleted for {id}')
    await sleep(1)
    await message.delete()

@client.command()
async def passgen(ctx):
    alphabet = string.ascii_letters
    token = ''.join(secrets.choice(alphabet) for i in range(20))
    await ctx.send(f'Pass: ||{token}||')

@client.command()
async def dmall(ctx, *, message: str):
    for user in client.user.friends:
        if blacklist.find_one({"_id": user.id}):
            pass
        else:
            await user.send(message)

    message = await ctx.send(f'DMing all Friends with ``{message}``')
    await sleep(1)
    await message.delete()

@commands.command()
async def dmbl(ctx, id: int):
    if not blacklist.find_one({"_id": id}):
        blacklisted = {"_id": id}
        blacklist.insert_one(blacklisted)

        message = await ctx.send(f'added {id} to the blacklist')
        await sleep(1)
        await message.delete()

    else:
        message = await ctx.send(f'is already {id} blacklisted')
        await sleep(1)
        await message.delete()

@commands.command()
async def dmubl(ctx, id: int):
    if not blacklist.find_one({"_id": id}):
        blacklist.delete_one({"_id": id})

        message = await ctx.send(f'removed {id} from the blacklist')
        await sleep(1)
        await message.delete()

    else:
        message = await ctx.send(f'{id} is not blacklisted')
        await sleep(1)
        await message.delete()

@client.command(aliases=["purge"])
async def clear(ctx, limit: int=None):
    async for msg in ctx.message.channel.history(limit=limit):
        if msg.author.id == client.user.id:
            try:
                await msg.delete()
            except:
                pass

@client.command()
async def spam(ctx, time:int, *, message):
    for i in range(time):
        await ctx.send(message)

@client.command()
async def cares(ctx):
    while True: 
        commands = [",help", ",afk", ",ping"]
        await ctx.send(random.choice(commands))

@client.command()
async def hell(ctx):
    while True: 
        commands = ["hell", "bleed"]
        await ctx.send(random.choice(commands))

@client.event
async def on_message(message):
    if '-' in message.content and not message.author.id != client.user.id:
        pass

    if '-' in message.content and message.author.id == client.user.id:
        await client.process_commands(message)
        await message.delete()

    else:
        try:
            async for message in message.channel.history(limit=1):
                if message.author.id != client.user.id:
                    if collection.find_one({"_id": message.author.id}):
                        message_respond = collection.find_one({"_id": message.author.id})["message"]
                        
                        if '+' in message_respond:
                            responds = []

                            for i in message_respond.split('+'):
                                responds.append(i)

                            await message.reply(random.choice(responds))

                        else:
                            await message.reply(message_respond)
        except:
            pass

client.run("MTg4MjUzMDc0MzQ5ODgzMzky.GdONO_.Tk6F1UEN7Asv5scbZ_SHzFTJ-ioDtGIV2QqSnU", bot=False)