import discord
from discord.ext import commands

class Moderate(commands.CommandError):
    def __init__(self, string):
        self.string = string
        super().__init__(f"You want to {string} 0 members? Use the help command to see how to use the command.")
        
class Perm(commands.CommandError):
    def __init__(self, perms):
        self.perms = perms
        super().__init__(f"you dont have {', '.join(perms).replace('_', ' ')} permissions")
        
class Var(commands.CommandError):
    def __init__(self, var):
        self.var = var
        super().__init__(f"you don't provide **{var}**, use help to view usage")
