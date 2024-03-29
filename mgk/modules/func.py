import discord
from discord.ext import commands
from mgk.bot import MGK
from discord.ext.commands.core import check
from discord.ext.commands.errors import *
from modules.errors import *

bot = MGK()

class general:
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
    @staticmethod
    def ownerOnly():
        async def predicate(ctx) -> bool:
            if not await ctx.bot.is_owner(ctx.author):
                raise NotOwner(f"{ctx.author.name} tried to run a owner only command")
            return True
        return check(predicate)
        
class member:
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
  
    @staticmethod
    def has_perm(*perms):
        async def predicate(ctx) -> bool:
            perms_miss = [perm for perm in perms if not getattr(ctx.permissions, perm)]
            if not perms_miss:
                return True
            raise Perm(perms_miss)
        return check(predicate)

