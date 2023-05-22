import json
import discord
import datetime
import aiosqlite

from discord import ui
from discord.ext import commands
from discord.ext import tasks
from discord.ui import Button, View
import button_paginator as pg

class usernames(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        setattr(self.bot, "db", await aiosqlite.connect("main.db"))
        async with self.bot.db.cursor() as cursor:
            await cursor.execute("CREATE TABLE IF NOT EXISTS oldusernamess (username TEXT, discriminator INTEGER, time INTEGER, user INTEGER)")
        await self.bot.db.commit()

    @commands.command(aliases = ['names', 'usernames'])
    async def pastusernames(self, ctx, member: discord.User = None):
        try:
            if member == None:
                member = ctx.author
            async with self.bot.db.cursor() as cursor:
                await cursor.execute("SELECT username, discriminator, time FROM oldusernamess WHERE user = ?", (member.id,))
                data = await cursor.fetchall()
                i=0
                page = 1
                k=1
                l=0
                mes = ""
                embeds = []
                messages = []
                if data:
                    for table in data[::-1]:
                        username = table[0]
                        discrim = table[1]
                        mes = f"{mes}`{k}` {username}#{discrim} — <t:{int(table[2])}:R>\n"
                        k+=1
                        l+=1
                        if l == 10:
                            messages.append(mes)
                            i+=1
                            embeds.append(discord.Embed(color=0x2f3136, description=messages[i]).set_author(name = f"{member.name}'s past usernames", icon_url = member.avatar).set_footer(text = f"{page}/{int(len(data)/10)+1 if len(data)/10 > int(len(data)/10) and int(len(data)/10) < int(len(data)/10)+1 else int(len(data)/10)} ({len(data)} entries)"))
                            page += 1
                            mes = ""
                            l=0
                    messages.append(mes)
                    embeds.append(discord.Embed(color=0x2f3136, description=messages[i]).set_author(name = f"{member.name}'s past usernames", icon_url = member.avatar).set_footer(text = f"{page}/{int(len(data)/10)+1 if len(data)/10 > int(len(data)/10) and int(len(data)/10) < int(len(data)/10)+1 else int(len(data)/10)} ({len(data)} entries)"))
                    paginator = pg.Paginator(self.bot, embeds, ctx, invoker=ctx.author.id)
                    paginator.add_button('prev')
                    paginator.add_button('delete')
                    paginator.add_button('next')
                    await paginator.start()
                else:
                    await ctx.reply(f"no logged usernames for {member}")
        except Exception as e:
            print(e)

 
    @commands.command()
    async def clearnames(self, ctx):
        try:
            async with self.bot.db.cursor() as cursor:
                await cursor.execute("DELETE FROM oldusernamess WHERE user = ?", (ctx.author.id,))
            await ctx.reply("👍")
            await self.bot.db.commit()
        except Exception as e:
            print(e)

    @commands.Cog.listener()
    async def on_user_update(self, before, after):
        try:
            async with self.bot.db.cursor() as cursor:
                await cursor.execute("SELECT user FROM nodata WHERE user = ?", (before.id,))
                data = await cursor.fetchone()
                if data:
                    pass
                else:
                    if before.name == after.name:
                        return
                    else:
                            await cursor.execute("INSERT INTO oldusernamess (username, discriminator, time, user) VALUES (?, ?, ?, ?)", (before.name, before.discriminator, int(datetime.datetime.now().timestamp()), before.id,))
                            await self.bot.db.commit()
        except Exception as e:
            print(e)


async def setup(bot):
    await bot.add_cog(usernames(bot))