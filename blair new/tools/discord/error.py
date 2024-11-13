from discord.ext.commands import CommandInvokeError


class Error(CommandInvokeError):
    def __init__(self, message: str):
        self.message: str = message
