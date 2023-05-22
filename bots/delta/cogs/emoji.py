import discord
from discord.ext import commands
from discord.ext import tasks
from core.utils.views import Views
from typing import Union
import os
import aiohttp
import json
import requests
import random
import asyncio
import sys
import random

class emoji(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot

    @commands.command(pass_contenxt=True)
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.has_permissions(manage_emojis=True)    
    async def steal(self, ctx, emoji: discord.PartialEmoji=None, * , emojiname=None):
        if emoji == None:
            emb = discord.Embed(colour=0x2f3136, description="please provide a emoji to steal")
            await ctx.reply(embed=emb, mention_author=False)

        if ctx.author.guild_permissions.manage_emojis:
            if emojiname == None:
                emojiname = emoji.name
            else:
                text = emojiname.replace(" ", "_")

                r = requests.get(emoji.url, allow_redirects=True)

            if emoji.animated == True:
                open("emoji.gif", "wb").write(r.content)
                with open("emoji.gif", "rb") as f:
                    z = await ctx.guild.create_custom_emoji(name=emojiname, image=f.read())
                os.remove("emoji.gif")

            else:
                open("emoji.png", "wb").write(r.content)
                with open("emoji.png", "rb") as f:
                    z = await ctx.guild.create_custom_emoji(name=emojiname, image=f.read())
                os.remove("emoji.png")

            embed = discord.Embed(description=f""" successfully stole {z} as "{emojiname}" """, color=0x2f3136)
            await ctx.reply(embed=embed, mention_author=False)
            
    @steal.error
    async def steal_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
            description = "This command requires `manage_emojis` permission",
            colour = 0xff0000
            )
            await ctx.reply(embed=embed, mention_author=False)
            
    @commands.command(aliases=['makesticker', 'create_sticker', 'make_sticker', 'create-sticker', 'make-sticker'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.has_permissions(manage_emojis_and_stickers=True)
    @commands.bot_has_permissions(manage_emojis_and_stickers=True)
    async def createsticker(self, ctx: commands.Context, emoji:[Union[discord.Emoji, discord.PartialEmoji]] = None):
        if emoji is not None:
            file = discord.File(BytesIO(await emoji.read()), filename=f"{emoji.name}.png")
        else:
            if len(ctx.message.attachments) == 0:
                await ctx.send(f"Please provide a sticker")
            else:
                file = await ctx.message.attachments[0].to_file()

        if not emoji_flags:
            name = file.filename.split(".")[0]
            description = f"Uploaded by {ctx.author}"
            emoji = name
        else:
            name = emoji.name if emoji_flags.name is None else emoji_flags.name if len(emoji_flags.name) > 1 else "name"
            description = emoji_flags.description if emoji_flags.description is not None else f"Uploaded by {ctx.author}"
            emoji = emoji_flags.emoji or name

        try:
            sticker = await ctx.guild.create_sticker(
              name=name,
              description=description,
              emoji=emoji,
              file=file,)
            return await ctx.reply(f"Sticker uploaded!", stickers=[sticker])
        except Exception as e:
            return await ctx.reply(f"Sticker Upload Error: `{e}")
            
async def setup(bot):
    await bot.add_cog(emoji(bot))