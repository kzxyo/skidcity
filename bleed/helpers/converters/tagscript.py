from discord.ext.commands import Converter

from helpers import tagscript
from helpers.managers import Context
from helpers.models.tagscript import ScriptObject


class TagScript(Converter):
    async def convert(self, ctx: Context, argument: str) -> ScriptObject:
        script: ScriptObject = tagscript.parse(
            script=argument,
            user=ctx.author,
            channel=ctx.channel,
        )

        return script
