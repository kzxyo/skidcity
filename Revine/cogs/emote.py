# This source code is 100% original, any contents will be credited in revine's credits command. Created by fsb#1337 & report#0001

from io import BytesIO
import discord, time, os, requests
from discord.ext import commands
from discord.ui import View, Button
from classes import Emotes, Colors

start_time = time.time()

async def get(session: object, url: object) -> object:
    async with session.get(url) as response:
        return await response.text()


class emote(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
        
# --------------------------------------------------------------------------------------- Addemoji
        
    @commands.command(aliases=["addemote", "ae", "stealemote", "stealemoji", "se", "steal"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.has_permissions(manage_emojis=True)    
    async def addemoji(self, ctx, emoji: discord.PartialEmoji = None, *, emojiname = None):
        if emoji == None:
            customemote = discord.Embed(description=f"{Emotes.warning_emote} {ctx.author.mention}: Custom Emoji is required.", color=Colors.normal)
            await ctx.send(embed=customemote)
            return
        if emojiname == None:
            emotename = discord.Embed(description=f"{Emotes.warning_emote} {ctx.author.mention}: Custom Emoji is required.", color=Colors.normal)
            await ctx.send(embed=emotename)
            return
        if ctx.author.guild_permissions.manage_emojis:
            if emojiname == None:
                emojiname = emoji.name
            else:
                text = emojiname.replace(" ", "_")
                r = requests.get(emoji.url, allow_redirects=True)
            if emoji.animated == True:
                open("emoji.gif", "wb").write(r.content)
                with open("emoji.gif", "rb") as f:
                    emote = await ctx.guild.create_custom_emoji(name=emojiname, image=f.read())
                os.remove("emoji.gif")
            else:
                open("emoji.png", "wb").write(r.content)
                with open("emoji.png", "rb") as f:
                    emote = await ctx.guild.create_custom_emoji(name=emojiname, image=f.read())
                os.remove("emoji.png")
        emoji = discord.Embed(description=f"{ctx.author.mention}: Added {emote} as ` {emojiname} `", color=Colors.normal)
        emoji.set_footer(text=f"category: {ctx.command.cog_name}・revine ©️ 2023")
        await ctx.send(embed=emoji)
        
# --------------------------------------------------------------------------------------- Enlarge

    @commands.command(aliases=["el", "enlargeemoji", "enlargeemote"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def enlarge(self, ctx, emoji: discord.PartialEmoji = None):
        if emoji == None:
            el = discord.Embed(description=f"{Emotes.warning_emote} {ctx.author.mention}: Please add a custom emoji.", color=Colors.normal)
            el.set_footer(text="category: emote・revine ©️ 2023")
            await ctx.send(embed=el)
            return
        emoteurl = emoji.url
        downloadbutton = Button(label="Download", url=emoteurl, emoji=Emotes.link_emote)
        embed = discord.Embed(color=Colors.normal)
        embed.set_image(url=emoteurl)
        embed.set_author(name=f"Enlarged: {emoji.name}")
        embed.set_footer(text="category: emote・revine ©️ 2023")
        view = View()
        view.add_item(downloadbutton)
        await ctx.send(view=view, embed=embed)
        
    @enlarge.error
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.PartialEmojiConversionFailure):
            e = discord.Embed(color=Colors.normal, description=f"{Emotes.warning_emote} {ctx.author.mention}: Cannot enlarge the provided emoji.")
            await ctx.reply(embed=e, mention_author=False)
            
            
    @commands.command(aliases=['emoteinfo', 'aboutemoji', 'aboutemote'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def emojiinfo(self, ctx, emoji: discord.PartialEmoji = None):
        if emoji == None:
            embed = discord.Embed(description=f"{Emotes.warning_emote} {ctx.author.mention}: Please add a custom emoji.", color=Colors.normal)
            embed.set_footer(text="category: emote・revine ©️ 2023")
            await ctx.send(embed=embed)
            return
        downloadbutton = Button(label="Download", emoji=Emotes.link_emote, url=f"{emoji.url}")
        embed = discord.Embed(description=f"**Animated:** ` {emoji.animated} `\n**Created:** <t:{int(emoji.created_at.timestamp())}:R>\n**ID:** ` {emoji.id} `")
        embed.set_thumbnail(url=f"{emoji.url}")
        embed.set_footer(text="category: emote・revine ©️ 2023")
        embed.set_author(name=f"Emote: {emoji.name}", icon_url=f"{emoji.url}")
        view = View()
        view.add_item(downloadbutton)
        await ctx.reply(view=view, embed=embed)
        
        
    @emojiinfo.error
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.PartialEmojiConversionFailure):
            e = discord.Embed(color=Colors.normal, description=f"{Emotes.warning_emote} {ctx.author.mention}: Cannot find information from the provided emoji.")
            await ctx.reply(embed=e, mention_author=False)
    
async def setup(bot) -> None:
    await bot.add_cog(emote(bot))