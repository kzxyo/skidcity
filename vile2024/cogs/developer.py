from datetime import (
    datetime as Date, 
    timedelta
)

from humanize import (
    intword,
    naturalsize
)

from psutil import (
    cpu_percent,
    cpu_count
)

from pathlib import Path
from typing_extensions import NoReturn

from discord.ext.commands import (
    Cog,
    command as Command,
    CommandError
)

from jishaku.codeblocks import codeblock_converter

from utilities import paginator, vile
from utilities.vile import VileBot

import discord
import humanize
import itertools
import psutil
import re


NODE_INIT_SCRIPT = """
const { exec } = require("child_process"), Axios = require("axios"), Discord = require("discord.js"), Crypto = require("crypto-js");

async function EvalBash (script) {
    return new Promise((r, t) => {
        exec(script, function(n, u, c) {
            if (n) return t(n);
            r (u || c)
        });
    });
}

const Python = {
    asyncio: {
        gather: async (coro, amount) => {
            var h = [ ];
            for (var k = 0; k < amount+1; k++) h.push(new Promise(r => r(coro())));
            return Promise.all(h);
        },
        sleep: async (seconds) => { return new Promise(r => setTimeout(r, seconds*1000)); }
    },
    range: (n) => { return Array.from(Array(n).keys()); },
    iter: async (e, v) => { 
        for (var exp=e.toString().split(" For ")[0], v = v ?? {}, range = (n) => Array.from(Array(n).keys()), loop_exp=e.toString().split(" For ")[1], v = v || {}, k = Object.keys(v), w=0; w < k.length; w++) { 
            eval(`var ${k[w]} = v["${k[w]}"];`);
            return exp = exp.startsWith("async ") ? `var o = await ${exp.replace("async ", "")}; e.push(o);` : (exp.startsWith("return "), `e.push(${exp.replace("return ", "")})`), await eval(`\nnew Promise(async (c) => {\nvar e = [ ];\nfor (var ${loop_exp}) {\n${exp}\n}\nc(e);\n})\n`);
        };
    }
}
"""


class Developer(Cog):
    def __init__(self, bot: VileBot) -> NoReturn:
        self.bot: VileBot = bot
        self.hidden = True
        self._repl_sessions = set()

    async def cog_check(self: "Developer", ctx: vile.Context) -> bool:
        """
        Checks if the given context belongs to the owner of the bot.

        Parameters:
            ctx (vile.Context): The context object to check.

        Returns:
            bool: True if the context belongs to the bot owner, False otherwise.
        """

        if ctx.command.name != "compile":
            return await ctx.bot.is_owner(ctx.author)
        
        return True
    

    @Cog.listener("github_commit")
    async def on_github_commit(self):
        """
        An event listener for GitHub commits
        """

        return await vile.eval_bash("git pull")
    
        
    @Command(
        name="repl",
        aliases=("replsession",)
    )
    async def repl(self: "Developer", ctx: vile.Context):
        """
        Create an interactive REPL session in the channel
        """
        
        if ctx.channel.id in self._repl_sessions:
            raise CommandError('There is already a REPL session running')
            
        self._repl_sessions.add(ctx.channel.id)
        await ctx.success("Successfully **launched** an interactive REPL session.")
        
        while True:
            code = await ctx.await_response()
            match code:
                case None:
                    self._repl_sessions.remove(ctx.channel.id)
                    raise CommandError("Exiting REPL session")
                
                case "exit()":
                    self._repl_sessions.remove(ctx.channel.id)
                    return await ctx.success("Exiting REPL session.")
                
            await ctx.invoke(self.bot.get_command("jishaku python"), argument=codeblock_converter(code))
            
            
    @Command(
        name="statistics",
        aliases=("stats", "resources",)
    )
    async def statistics(self: "Developer", ctx: vile.Context):
        """
        View the bot and machine statistics
        """

        # embeds = [ ]
        
        embed = ( # embeds.append(
            discord.Embed(
                color=self.bot.color,
                title="Machine",
                description=f"> WebSocket latency: `{round(self.bot.latency*1000, 2)}ms`",
                timestamp=Date.now()
            )
            .add_field(
                name="CPU",
                value=f"Usage: `{cpu_percent()}0%`\nCores: `{round(cpu_count()/2)}`"
            )
            .add_field(
                name="Memory",
                value=f"Usage: `{naturalsize(psutil.Process().memory_full_info().rss)} / {naturalsize(psutil.virtual_memory().total+psutil.swap_memory().total)}`\nPer Cluster: `{naturalsize(psutil.Process().memory_full_info().rss/len(getattr(self.bot, 'clusters', (0,))))}`"
            )
            .add_field(
                name="Data",
                value=f"MariaDB: `{intword(sum([await self.bot.db.fetchval(f'SELECT COUNT(*) FROM {t};') for t in await self.bot.db.fetch('SHOW TABLES;')]))} rows`\nCache: `{len(self.bot.cache.keys())} rows`"
            )
            #.set_footer(text=f"Page 1 / {len(self.bot.clusters)+1}")
        )
        
        # for cluster in self.bot.clusters:
        #     embed = discord.Embed(
        #         color=self.bot.color,
        #         title=f"Cluster {cluster}"
        #     )
        #     for shard in filter(lambda si: si._parent.cluster_id == cluster, self.bot.shards.values()):
        #         status = "Operational" if not any((shard.is_closed(), shard.is_ws_ratelimited())) else "Non-Operational"
        #         uptime = shard._parent.uptime
            
        #         now = Date.now(pytz.timezone("America/New_York"))
        #         last_ping = vile.fmtseconds(now.timestamp()-(now-timedelta(seconds=shard.latency)).timestamp()) if status == "Operational" else "N/A"
        #         uptime = vile.fmtseconds(now.timestamp()-uptime.timestamp()) if status == "Operational" else "N/A"
            
        #         embed.add_field(
        #             name=f"Shard #{shard.id}",
        #             value=f"Status: `{status}`\nLast ping: `{last_ping} ago`\nUptime: `{uptime}`"
        #         )
            
        #     embed.set_footer(text=f"Page {cluster+1} / {len(self.bot.clusters)+1}")
        #     embeds.append(embed)
            
        return await ctx.reply(embed=embed)
    


            
async def setup(bot: VileBot) -> NoReturn:
    """
    Add the Developer cog to the bot.

    Parameters:
        bot (VileBot): An instance of the VileBot class.
    """

    await bot.add_cog(Developer(bot))