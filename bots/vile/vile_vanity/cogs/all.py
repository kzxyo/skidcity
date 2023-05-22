from hashlib import new
import discord, os, sys, asyncio, datetime, textwrap, pathlib, typing, traceback, json, time, requests, random, humanize
from discord.ext import tasks, commands ; from datetime import datetime, timedelta, timezone ; from pathlib import Path;
from modules import paginator as pg
from vile_cfg import utils

class all(commands.Cog):

    def __init__(self, bot): 
        
        self.bot = bot
        #
        self.done = self.bot.done
        self.fail = self.bot.fail
        self.warn = self.bot.fail
        self.reply = self.bot.reply
        self.dash = self.bot.dash
        #
        self.success = self.bot.color
        self.error = self.bot.color
        self.warning = self.bot.color

    @commands.Cog.listener()
    async def on_presence_update(self, before: discord.Member, after: discord.Member):

        #db = utils.read_json('boost')[str(after.guild.id)]
        #if after.guild.id != 998713201124450445: return
        user = after
        guild = after.guild
        try:
            db = utils.read_json('vanity')
            vanity = db[str(after.guild.id)]['vanity']
            try: ba = str(before.activity.name).lower()
            except: ba = 'none'
            try: aa = str(after.activity.name).lower()
            except: aa = 'none'
            if ba == aa: return
            if db[str(after.guild.id)]['vanity'] in aa and db[str(after.guild.id)]['vanity'] not in ba:
                try:
                    x = after.guild.get_role(db[str(after.guild.id)]['role'])
                    await after.add_roles(x, reason='vile vanity: vanity in status')
                except: pass
                try:
                    z = await after.guild.fetch_channel(db[str(after.guild.id)]['channel'])
                    await z.send(embed=discord.Embed(color=0x2f3136, title=after, description=f"{after.mention} {db[str(after.guild.id)]['message'].format(user=user, guild=guild, vanity=vanity)}").set_footer(text=f"{user.name} repped {db[str(after.guild.id)]['vanity']}"))
                except: pass
            elif db[str(after.guild.id)]['vanity'] not in aa and db[str(after.guild.id)]['vanity'] in ba:
                try:
                    x = after.guild.get_role(db[str(after.guild.id)]['role'])
                    await after.remove_roles(x, reason='vile vanity: vanity removed from status')
                except: pass

        except:
            #traceback.print_exc()
            pass


    @commands.hybrid_group(name='vanity', aliases=['v'], invoke_without_command=True)
    @commands.has_permissions(manage_guild=True)
    async def vanity(self, ctx):

        subcmds = ",vanity clear\n,vanity role\n,vanity channel\n,vanity message"
        subcmds = f"```{subcmds}```"
        note1 = discord.Embed(color=utils.color('main'), timestamp=datetime.now())
        note1.set_author(name=f"vanity", icon_url=self.bot.user.display_avatar)
        note1.add_field(name=f"{self.dash} Info", value=f"{self.reply} **description:** manage the guild's vanity role\n{self.reply} **aliases:** v")  
        note1.add_field(name=f"{self.dash} Sub Cmds", value=subcmds, inline=False)
        note1.set_footer(text=f"config", icon_url='https://cdn.discordapp.com/emojis/998805272468390048.gif?size=4096&quality=lossless')
        await ctx.reply(embed=note1)

    @vanity.command(name='clear')
    @commands.has_permissions(manage_guild=True)
    async def vanity_clear(self, ctx):

        try:
            db = utils.read_json('vanity')
            db.pop(str(ctx.guild.id))
            utils.write_json(db, 'vanity')
        except:
            pass
        await ctx.reply(':thumbsup:')

    @vanity.command(name='role')
    @commands.has_permissions(manage_guild=True)
    async def vanity_role(self, ctx, *, role: discord.Role=None):

        try:
            db = utils.read_json('vanity')
            db[str(ctx.guild.id)]['role'] = role.id 
            utils.write_json(db, 'vanity')
        except:
            db = utils.read_json('vanity')
            db[str(ctx.guild.id)] = {}
            utils.write_json(db, 'vanity')
            db = utils.read_json('vanity')
            db[str(ctx.guild.id)]['role'] = role.id
            db[str(ctx.guild.id)]['channel'] = None
            db[str(ctx.guild.id)]['message'] = None
            db[str(ctx.guild.id)]['vanity'] = None
            utils.write_json(db, 'vanity')
        await ctx.send(':thumbsup:')

    @vanity.command(name='channel')
    @commands.has_permissions(manage_guild=True)
    async def vanity_channel(self, ctx, *, channel: discord.TextChannel):

        try:
            db = utils.read_json('vanity')
            db[str(ctx.guild.id)]['channel'] = channel.id 
            utils.write_json(db, 'vanity')
        except:
            db = utils.read_json('vanity')
            db[str(ctx.guild.id)] = {}
            utils.write_json(db, 'vanity')
            db = utils.read_json('vanity')
            db[str(ctx.guild.id)]['role'] = None
            db[str(ctx.guild.id)]['channel'] = channel.id
            db[str(ctx.guild.id)]['message'] = None
            db[str(ctx.guild.id)]['vanity'] = None
            utils.write_json(db, 'vanity')
        await ctx.send(':thumbsup:')

    @vanity.command(name='message')
    @commands.has_permissions(manage_guild=True)
    async def vanity_message(self, ctx, *, message: str=None):

        try:
            db = utils.read_json('vanity')
            db[str(ctx.guild.id)]['message'] = message 
            utils.write_json(db, 'vanity')
        except:
            db = utils.read_json('vanity')
            db[str(ctx.guild.id)] = {}
            utils.write_json(db, 'vanity')
            db = utils.read_json('vanity')
            db[str(ctx.guild.id)]['role'] = None
            db[str(ctx.guild.id)]['channel'] = None
            db[str(ctx.guild.id)]['message'] = message
            db[str(ctx.guild.id)]['vanity'] = None
            utils.write_json(db, 'vanity')
        await ctx.send(':thumbsup:')

    @vanity.command(name='set')
    @commands.has_permissions(manage_guild=True)
    async def vanity_set(self, ctx, vanity: str=None):

        try:
            db = utils.read_json('vanity')
            db[str(ctx.guild.id)]['vanity'] = vanity 
            utils.write_json(db, 'vanity')
        except:
            db = utils.read_json('vanity')
            db[str(ctx.guild.id)] = {}
            utils.write_json(db, 'vanity')
            db = utils.read_json('vanity')
            db[str(ctx.guild.id)]['role'] = None
            db[str(ctx.guild.id)]['channel'] = None
            db[str(ctx.guild.id)]['message'] = None
            db[str(ctx.guild.id)]['vanity'] = vanity
            utils.write_json(db, 'vanity')
        await ctx.send(':thumbsup:')

    @commands.Cog.listener()
    async def on_guild_join(self, guild):

        if guild.member_count < 20:
            await guild.leave()
        if guild.premium_subscription_count < 14:
            await guild.leave()

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):

        if isinstance(error, commands.BotMissingPermissions):
            permissions = '\n'.join([x.lower() for x in error.missing_permissions])
            permissions = permissions.replace('_', ' ')
            await ctx.reply(embed=discord.Embed(color=utils.color('warn'), description=f"{utils.emoji('warn')} {ctx.author.mention}**:** i'm missing the **{permissions}** permission"))

        elif isinstance(error, commands.MissingPermissions):
            permissions = '\n'.join([i.lower() for i in error.missing_permissions])
            permissions = permissions.replace('_', ' ')
            await ctx.reply(embed=discord.Embed(color=utils.color('warn'), description=f"{utils.emoji('warn')} {ctx.author.mention}**:** you're missing the **{permissions}** permission"))

async def setup(bot):
    await bot.add_cog(all(bot))