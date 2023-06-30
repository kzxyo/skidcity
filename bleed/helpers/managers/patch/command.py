from discord.ext.commands.core import Command, hooked_wrapped_callback

from helpers.managers import Context
from helpers.models.tagscript import ScriptObject


class CommandCore(Command):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    async def invoke(self, ctx: Context, /) -> None:
        await self.prepare(ctx)

        if ctx.kwargs and (FlagConverter := getattr(ctx.command, "flags", None)):
            kwarg, argument = list(ctx.kwargs.keys())[-1], list(ctx.kwargs.values())[-1]

            if argument == None or isinstance(argument, (str, ScriptObject)):
                parsed = await FlagConverter.convert(
                    ctx, str(argument).replace("—", "")
                )

                for name, value in parsed:
                    ctx.flags[name] = value
                    names = [name]
                    if aliases := parsed.get_flags()[name].aliases:
                        names.extend(aliases)

                    for name in names:
                        if isinstance(argument, str):
                            ctx.kwargs.update(
                                {
                                    kwarg: (
                                        str(ctx.kwargs.get(kwarg))
                                        .replace("—", "--")
                                        .replace(f"--{name} {value}", "")
                                        .replace(f"--{name}", "")
                                        .strip()
                                    )
                                    or (
                                        ctx.command.params.get(kwarg).default
                                        if isinstance(
                                            ctx.command.params.get(kwarg).default, str
                                        )
                                        else None
                                    )
                                }
                            )

                        elif isinstance(argument, ScriptObject):
                            argument.script = (
                                argument.script.replace("—", "--")
                                .replace(f"--{name} {value}", "")
                                .replace(f"--{name}", "")
                                .strip()
                            )
                            ctx.kwargs.update(
                                {
                                    kwarg: argument
                                    or (
                                        ctx.command.params.get(kwarg).default
                                        if isinstance(
                                            ctx.command.params.get(kwarg).default, str
                                        )
                                        else None
                                    )
                                }
                            )

        ctx.invoked_subcommand = None
        ctx.subcommand_passed = None
        injected = hooked_wrapped_callback(self, ctx, self.callback)
        await injected(*ctx.args, **ctx.kwargs)


Command.invoke = CommandCore.invoke
