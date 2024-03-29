import discord, datetime, humanfriendly
from discord.ext import commands
from modules.func import member
from mgk.cfg import E
from modules.errors import *

class moderation(commands.Cog, description = "see moderation commands"):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(extras={"Category": "Moderation"}, usage="ban **member(s) | *reason", help="ban a member or more without delete user messages")
    @member.has_perm("ban_members")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def ban(self, ctx, *, arg=None):
        if not arg:
            raise Moderate("ban")
        split = arg.split("|", 1)
        reason = split[1].strip() if len(split) > 1 else "no reason"
        reasonban = f"banned by {ctx.author} for {reason}"
        members = split[0].split()
        b = []
        e = []
        ids = []
        for i in members:
            if i.startswith("<@") and i.endswith(">"):
                id = int(i[2:-1])
                ids.append(id)
            elif i.isdigit():
                ids.append(int(i))
            else:
                m = discord.utils.find(lambda mem: mem.name.lower().startswith(i.lower()), ctx.guild.members).id
                ids.append(m)
        for i in ids:
            if ctx.guild.get_member(i) is not None:
                if ctx.check_member(ctx.guild.get_member(i), ctx.guild):
                    m = ctx.guild.get_member(i)
                    e.append(m.mention)
                else:
                    try:
                        member = ctx.guild.get_member(i)
                        await member.ban(delete_message_seconds=0, reason=reasonban)
                        b.append(member.mention)
                    except:
                        if ctx.guild.get_member(i) is not None:
                            member = ctx.guild.get_member(i)
                            e.append(member.mention)
                        else:
                            e.append(str(i))
        msg = None
        if b and not e:
            msg = f"{E.ban} {', '.join(b)} for {reason}"
            await ctx.succes(msg)
        if e and b:
            msg = f"{E.ban} {', '.join(b)} for {reason} and {', '.join(e)} can't be banned"
            await ctx.succes(msg)
        elif e and not b:
            msg = f"{', '.join(e)} can't be banned"
            await ctx.error(msg)
            
    @commands.command(extras={"Category": "Moderation"}, usage="hardban **member(s) | *reason", help="ban a member or more deleting the messages from the last week")
    @member.has_perm("ban_members")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def hardban(self, ctx, *, arg=None):
        if not arg:
            raise Moderate("hardban")
        split = arg.split("|", 1)
        reason = split[1].strip() if len(split) > 1 else "no reason"
        reasonban = f"hardbanned by {ctx.author} for {reason}"
        members = split[0].split()
        b = []
        e = []
        ids = []
        for i in members:
            if i.startswith("<@") and i.endswith(">"):
                id = int(i[2:-1])
                ids.append(id)
            elif i.isdigit():
                ids.append(int(i))
            else:
                m = discord.utils.find(lambda mem: mem.name.lower().startswith(i.lower()), ctx.guild.members).id
                ids.append(m)
        for i in ids:
            if ctx.guild.get_member(i) is not None:
                if ctx.check_member(ctx.guild.get_member(i), ctx.guild):
                    m = ctx.guild.get_member(i)
                    e.append(m.mention)
                else:
                    try:
                        member = ctx.guild.get_member(i)
                        await member.ban(reason=reasonban)
                        b.append(member.mention)
                    except:
                        if ctx.guild.get_member(i) is not None:
                            member = ctx.guild.get_member(i)
                            e.append(member.mention)
                        else:
                            e.append(str(i))
        msg = None
        if b and not e:
            msg = f"{E.ban} {', '.join(b)} for {reason}"
            await ctx.succes(msg)
        if e and b:
            msg = f"{E.ban} {', '.join(b)} for {reason} and {', '.join(e)} can't be banned"
            await ctx.succes(msg)
        elif e and not b:
            msg = f"{', '.join(e)} can't be banned"
            await ctx.error(msg)
            
    @commands.command(extras={"Category": "Moderation"}, usage="untimeout !member", help="untimeout a member")
    @member.has_perm("moderate_members")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def untimeout(self, ctx, member: discord.Member=None):
        if not member:
            raise Moderate("untimeout")
        if not member.is_timed_out():
            return await ctx.error("this command can be used on timeouted members, you want to untimeout members which isn't timeouted?")
        await member.edit(timed_out_until=None, reason=f"untimed out by {ctx.author.name}")
        await ctx.succes(f"{member.mention} was untimed out")
        
    @commands.command(extras={"Category": "Moderation"}, usage="timeout !member !time", help="timeout a member")
    @member.has_perm("moderate_members")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def timeout(self, ctx, member: discord.Member=None, time: str=None):
        if not member:
            raise Moderate("timeout")
        if not time:
            raise Var("time")
        if ctx.check_member(member, ctx.guild):
            return await ctx.error(ctx.check_member(member, ctx.guild))
        seconds = humanfriendly.parse_timespan(time)
        time = discord.utils.utcnow() + datetime.timedelta(seconds=seconds)
        await member.timeout(time, reason=f"timed out by {ctx.author.name}")
        await ctx.succes(f"{member.mention} was timed out")
        
    @commands.command(extras={"Category": "Moderation"}, usage="unban !user id", help="unban a user")
    @member.has_perm("ban_members")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def unban(self, ctx, *, user: str=None):
        if user is None:
            raise Moderate("unban")
        if user.isdigit() == False:
            return await ctx.error("you can only unban a user with user id")
        banned = await self.bot.http.get(f"https://discord.com/api/v7/guilds/{ctx.guild.id}/bans/{user}", headers={"Authorization": f"Bot {self.bot.http.token}"})
        if banned == 404:
            await ctx.error("this user is not banned")
        else:
            data = banned['user']
            await ctx.guild.unban(discord.Object(data['id']))
            await ctx.succes(f"{data['username']} was unbanned")
            
    @commands.command(extras={"Category": "Moderation"}, usage="kick **member(s) | *reason", help="kick a member or more")
    @member.has_perm("kick_members")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def kick(self, ctx, *, arg=None):
        if not arg:
            raise Moderate("kick")
        split = arg.split("|", 1)
        reason = split[1].strip() if len(split) > 1 else "no reason"
        reasonkick = f"kicked by {ctx.author} for {reason}"
        members = split[0].split()
        b = []
        e = []
        ids = []
        for i in members:
            if i.startswith("<@") and i.endswith(">"):
                id = int(i[2:-1])
                ids.append(id)
            elif i.isdigit():
                ids.append(int(i))
            else:
                m = discord.utils.find(lambda mem: mem.name.lower().startswith(i.lower()), ctx.guild.members).id
                ids.append(m)
        for i in ids:
            if ctx.guild.get_member(i) is not None:
                if ctx.check_member(ctx.guild.get_member(i), ctx.guild):
                    m = ctx.guild.get_member(i)
                    e.append(m.mention)
                else:
                    try:
                        member = ctx.guild.get_member(i)
                        await member.kick(reason=reasonkick)
                        b.append(member.mention)
                    except:
                        if ctx.guild.get_member(i) is not None:
                            member = ctx.guild.get_member(i)
                            e.append(member.mention)
                        else:
                            e.append(str(i))
        msg = None
        if b and not e:
            msg = f"kicked {', '.join(b)} for {reason}"
            await ctx.succes(msg)
        if e and b:
            msg = f"kicked {', '.join(b)} for {reason} and {', '.join(e)} can't be kicked"
            await ctx.succes(msg)
        elif e and not b:
            msg = f"{', '.join(e)} can't be kicked"
            await ctx.error(msg)
            
    @commands.command(extras={"Category": "Moderation"}, usage="permmute !member", help="mute a member until someone unmute him")
    @member.has_perm("manage_roles")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def permmute(self, ctx, member: discord.Member=None):
        if member is None:
            raise Moderate('permmute')
        data = await self.bot.db.fetchone("SELECT role FROM muterole WHERE guild = %s", (ctx.guild.id,))
        if data is None:
            return await ctx.error("you dont have mute role seted use **muterole setup**")
        if ctx.check_member(member, ctx.guild):
            return await ctx.error(ctx.check_member(member, ctx.guild))
        role = ctx.guild.get_role(int(data['role']))
        await member.add_roles(role)
        await ctx.succes(f"{member.mention} is muted")
        
    @commands.command(extras={"Category": "Moderation"}, usage="unmute !member", help="unmute a member")
    @member.has_perm("manage_roles")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def unmute(self, ctx, member: discord.Member=None):
        if member is None:
            raise Moderate('unmmute')
        data = await self.bot.db.fetchone("SELECT role FROM muterole WHERE guild = %s", (ctx.guild.id,))
        if data is None:
            return await ctx.error("you dont have mute role seted use **muterole setup**")
        role = ctx.guild.get_role(int(data['role']))
        if not role in member.roles:
            return await ctx.error(f"{member.mention} is not muted")
        await member.remove_roles(role)
        await ctx.succes(f"{member.mention} is unmuted")

async def setup(bot):
    await bot.add_cog(moderation(bot))