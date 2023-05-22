import discord

from modules import default
from discord.ext import commands

owners = default.config()["owners"]
donors = default.config()["donors"]
kill = default.config()["kill"]
admins = default.config()["admins"]
dev = default.config()["dev"]



def is_owner(ctx):
    """ Checks if the author is one of the owners """
    return ctx.author.id in owners

def is_donor(ctx):
    return ctx.author.id in donors

def is_admin(ctx):
    role=bot.get_role(882549524176969739)
    return ctx.author.id in admins or member.id in role.members

def is_kill(ctx):
    """ Checks if the author is one of the owners """
    return ctx.author.id in kill

def is_dev(ctx):
    """ Checks if the author is one of the owners """
    return ctx.author.id in dev

def is_gowner(ctx):
    return ctx.author.id is ctx.guild.owner.id


async def check_permissions(ctx, perms, *, check=all):
    """ Checks if author has permissions to a permission """
    if ctx.author.id in owners:
        return True

    resolved = ctx.channel.permissions_for(ctx.author)
    return check(getattr(resolved, name, None) == value for name, value in perms.items())


def has_permissions(*, check=all, **perms):
    """ discord.Commands method to check if author has permissions """
    async def pred(ctx):
        return await check_permissions(ctx, perms, check=check)
    return commands.check(pred)


async def check_priv(ctx, member):
    """ Custom (weird) way to check permissions when handling moderation commands """
    try:
        # Self checks
        if member == ctx.author:
            return await ctx.send(f"You can't {ctx.command.name} yourself")
        if member.id == ctx.bot.user.id:
            return await ctx.send("So that's what you think of me huh..? sad ;-;")

        # Check if user bypasses
        if ctx.author.id == ctx.guild.owner.id:
            return False

        # Now permission check
        if member.id in owners:
            if ctx.author.id in owners:
                return await ctx.send(f"I can't {ctx.command.name} one of the protected server owners")
            else:
                pass
        if member.id in kill:
            if ctx.author.id in kill:
                return await ctx.send(f"I can't {ctx.command.name} the menace of cord")
            else:
                pass
        if member.id == ctx.guild.owner.id:
            return await ctx.send(f"You can't {ctx.command.name} the owner, lol")
        if ctx.author.top_role == member.top_role:
            return await ctx.send(f"You can't {ctx.command.name} someone who has the same permissions as you...")
        if ctx.author.top_role < member.top_role:
            return await ctx.send(f"Nope, you can't {ctx.command.name} someone higher than yourself.")
    except Exception:
        pass

    def escape_all(string, mentions = True, markdown = True):
        if mentions: string = discord.utils.escape_mentions(string)
        if markdown: string = discord.utils.escape_markdown(string)
        return string


    def name(self, member : discord.Member):
        # A helper function to return the member's display name
        return escape_all(member.display_name)

    def memberForID(self, checkid, server):
        try:
            return server.get_member(int(checkid)) if server else self.bot.get_user(int(checkid))
        except:
            return None

    def memberForName(self, name, server):
        mems = server.members if server else self.bot.users
        # Check nick first - then name
        name = str(name)
        for member in mems:
            if not hasattr(member,"nick"):
                # No nick property - must be a user, bail
                break
            if member.nick and member.nick.lower() == name.lower():
                return member
        for member in mems:
            if member.name.lower() == name.lower():
                return member
        mem_parts = name.split("#")
        if len(mem_parts) == 2:
            # We likely have a name#descriminator
            try:
                mem_name = mem_parts[0]
                mem_disc = int(mem_parts[1])
            except:
                mem_name = mem_disc = None
            if mem_name:
                for member in mems:
                    if member.name.lower() == mem_name.lower() and int(member.discriminator) == mem_disc:
                        return member
        mem_id = re.sub(r'\W+', '', name)
        new_mem = self.memberForID(mem_id, server)
        if new_mem:
            return new_mem
        
        return None


def can_handle(ctx, permission: str):
    """ Checks if bot has permissions or is in DMs right now """
    return isinstance(ctx.channel, discord.DMChannel) or getattr(ctx.channel.permissions_for(ctx.guild.me), permission)
