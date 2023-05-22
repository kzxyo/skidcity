import json
import discord
import datetime
import aiosqlite
import aiohttp
import io

from discord import ui
from discord.ext import commands
from discord.ext import tasks
from discord.ui import Button, View
import button_paginator as pg

async def file(url: str, fn: str=None, filename: str=None):

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as r:
                data=await r.read()

        fileName=''
        if not fn and not filename:
            fileName='image.png'
        elif not fn and filename:
            fileName=filename
        elif not filename and fn:
            fileName=fn
        elif filename and fn:
            return

        return discord.File(io.BytesIO(data), filename=fileName)
class avatars(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        setattr(self.bot, "db", await aiosqlite.connect("main.db"))
        async with self.bot.db.cursor() as cursor:
            await cursor.execute("CREATE TABLE IF NOT EXISTS avatars (user INTEGER, avatar TEXT)")
        await self.bot.db.commit()

    @commands.command(aliases = ['avatars', 'oldavatars', 'avatarhistory', 'ah', 'avs'])
    async def pastavatars(self, ctx, member: discord.User = None):
        try:
            if member == None:
                member = ctx.author
            async with self.bot.db.cursor() as cursor:
                await cursor.execute("SELECT avatar FROM avatars WHERE user = ?", (member.id,))
                data = await cursor.fetchall()
                embeds = []
                avatars = 0
                if data:
                    for table in data:
                        username = table[0]
                        avatars += 1
                        embed = discord.Embed(color = 0x2f3136)
                        embeds.append(discord.Embed(title=f"{member.name}'s avatars", color=0x2f3136).set_author(name = f"{member.name}", icon_url = member.avatar).set_footer(text = f"{avatars}/{len(data)}", icon_url = self.bot.user.avatar).set_image(url = username))
                    paginator = pg.Paginator(self.bot, embeds, ctx, invoker=ctx.author.id)
                    paginator.add_button('prev', emoji= "<:left:1018156480991612999>")
                    paginator.add_button('delete', emoji = "<:stop:1018156487232720907>")
                    paginator.add_button('next', emoji="<:right:1018156484170883154>")
                    await paginator.start()
                else:
                    await ctx.reply(f"no logged avatars for {member}")
        except Exception as e:
            print(e)

 
    @commands.command()
    async def clearavatars(self, ctx):
        try:
            async with self.bot.db.cursor() as cursor:
                await cursor.execute("DELETE FROM avatars WHERE user = ?", (ctx.author.id,))
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
                    if before.display_avatar != after.display_avatar:
                        logs = self.bot.get_channel(1044658984646361128)
                        file = await before.display_avatar.to_file(filename=f"{before.id}.{'png' if not before.display_avatar.is_animated() else 'gif'}")
                        msg = await logs.send(file =file)
                        await cursor.execute("INSERT INTO avatars (avatar, user) VALUES (?, ?)", (msg.attachments[0].proxy_url, before.id,))
                        await self.bot.db.commit()
        except:
            traceback.print_exc()


async def setup(bot):
    await bot.add_cog(avatars(bot))