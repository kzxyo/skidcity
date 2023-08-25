import discord, re, aiofiles, os, pytz, asyncio, humanize, psutil
from typing import Union
from datetime import datetime, timedelta
from discord.ext import commands
from pathlib import Path
from utilities import vile
from jishaku.codeblocks import codeblock_converter


NODE_INIT_SCRIPT = """
const { exec } = require("child_process"), Axios = require("axios"), Discord = require("discord.js"), Crypto = require("crypto-js");

async function Eval (script) {
    return new Promise((r, t) => {
        exec(script, function(n, u, c) {
            if(n) return t(n);
            r(u || c)
        });
    });
}

const Python = {
    asyncio: {
        gather: async (coro, amount) => {
            var h = [];
            for (var k = 0; k < amount+1; k++) h.push(new Promise(r => r(coro())));
            return Promise.all(h);
        },
        sleep: async (seconds) => { return new Promise(r => setTimeout(r, s*1000)); }
    },
    range: (n) => { return Array.from(Array(n).keys()); },
    iter: async (e, v) => { 
        for (var exp=e.toString().split(" For ")[0], v = v ?? {}, range = (n) => Array.from(Array(n).keys()), loop_exp=e.toString().split(" For ")[1], v = v || {}, k = Object.keys(v), w=0; w < k.length; w++) { 
            eval(`var ${k[w]} = v["${k[w]}"];`);
            return exp = exp.startsWith("async ") ? `var o = await ${exp.replace("async ", "")}; e.push(o);` : (exp.startsWith("return "), `e.push(${exp.replace("return ", "")})`), await eval(`\nnew Promise(async (c) => {\nvar e = [];\nfor (var ${loop_exp}) {\n${exp}\n}\nc(e);\n})\n`);
        };
    }
}
"""

class Developer(commands.Cog):
    def __init__(self, bot: vile.VileBot) -> None:
        self.bot = bot
        self.hidden = True
        self._repl_sessions = set()
        
        
    async def cog_check(self, ctx: vile.Context) -> bool:
        return await ctx.bot.is_owner(ctx.author)
        
        
    @commands.command(
        name="repl",
        aliases=("replsession",)
    )
    async def repl(self, ctx: vile.Context):
        """Create an interactive REPL session in the channel"""
        
        if ctx.channel.id in self._repl_sessions:
            return await ctx.error('There is already a REPL session running')
            
        self._repl_sessions.add(ctx.channel.id)
        await ctx.success("Successfully **launched** an interactive REPL session.")
        
        while True:
            code = await ctx.await_response()
            match code:
                case None:
                    self._repl_sessions.remove(ctx.channel.id)
                    return await ctx.error("Exiting REPL session")
                
                case "exit()":
                    self._repl_sessions.remove(ctx.channel.id)
                    return await ctx.success("Exiting REPL session.")
                
            await ctx.invoke(self.bot.get_command("jishaku python"), argument=codeblock_converter(code))
            
            
    @commands.group(
        name="evaluate",
        aliases=("eval", "exec",),
        usage="[sub command]",
        example="javascript console.log('hi');",
        invoke_without_command=True
    )
    async def evaluate(self, ctx: vile.Context, *, script: codeblock_converter):
        """Evaluate a Python script and return the output"""
        await ctx.invoke(self.bot.get_command("jishaku python"), argument=script)
        
        
    @evaluate.command(
        name="bash",
        aliases=("shell", "sh",),
        usage="<script>",
        example="halt"
    )
    async def evaluate_bash(self, ctx: vile.Context, *, script: str):
        """Evaluate a Bash script and return the output"""
        await ctx.invoke(self.bot.get_command("jishaku shell"), argument=codeblock_converter(script))
        

        
    @evaluate.command(
        name="javascript",
        aliases=("js",),
        usage="<script>",
        example="console.log('hi');"
    )
    async def evaluate_javascript(self, ctx: vile.Context, *, script: str):
        """Evaluate JavaScript and return the output"""
        
        source = Path(__name__).parent / "scaffolds" / "node"
        async with aiofiles.open(str(source / "index.js"), "r") as file:
            content = await file.read()
            
        content = content.replace("{content}", f"{NODE_INIT_SCRIPT}\n{script}")
        requirements = " ".join(f"npm install {match};" for match in re.findall('// require: (.+)', script))
        async with vile.TempFile(content.encode("utf-8"), directory=source, extension="js") as dummy:
            return await ctx.invoke(self.evaluate_bash, script=f"{requirements} node {dummy}")
            
        
    @evaluate.command(
        name="rust",
        aliases=("rs",),
        usage="<script>",
        example="fn main() { println!('hi'); }"
    )
    async def evaluate_rust(self, ctx: vile.Context, *, script: str):
        """Evaluate a Rust script and return the output"""
        
        source = Path(__name__).parent / "scaffolds" / "rust"
        async with aiofiles.open(str(source / "main.rs"), "r") as file:
            content = await file.read()
            
        content = content.format(content=script)
        requirements = " ".join(f"cargo add {match};" for match in re.findall('// require: (.+)', script))
        async with vile.TempFile(content.encode("utf-8"), directory=str(source), extension="rs") as dummy:
            other_dummy = dummy.split("/")[-1][:-3]
            await ctx.invoke(self.evaluate_bash, script=f"cd {source}; {requirements} rustc {dummy}; ./{other_dummy}")
            return os.remove(f"{source}/{other_dummy}")
            

    @evaluate.command(
        name="lolcode",
        aliases=("lol",),
        usage="<script>",
        example="""HAI 1.3\nVISIBLE "hello"\nKTHXBYE"""
    )
    async def evaluate_lolcode(self, ctx: vile.Context, *, script: str):
        """Evaluate a LolCode script and return the output"""
        
        try:
            output = await vile.eval_lolcode(script)
            return await ctx.invoke(self.bot.get_command("jishaku python"), argument=codeblock_converter(f"return '''{output}'''")) 
        except Exception as err:
            return await ctx.reply(f"```lol\n{err}```")
            
            
    @commands.command(
        name="statistics",
        aliases=("stats", "resources",)
    )
    async def statistics(self, ctx: vile.Context):
        """View the bot and machine statistics"""
        
        embeds = []
        
        embeds.append(
            discord.Embed(
                color=self.bot.color,
                title="Machine",
                description=f"> WebSocket latency: `{round(self.bot.latency*1000, 2)}ms`"
            )
            .add_field(
                name="CPU",
                value=f"Usage: `{psutil.cpu_percent()}0%`\nCores: `{round(psutil.cpu_count()/2)}`"
            )
            .add_field(
                name="Memory",
                value=f"Usage: `{humanize.naturalsize(psutil.Process().memory_full_info().rss)} / {humanize.naturalsize(psutil.virtual_memory().total+psutil.swap_memory().total)}`\nPer Cluster: `{humanize.naturalsize(psutil.Process().memory_full_info().rss/len(self.bot.clusters))}`"
            )
            .add_field(
                name="Data",
                value=f"MariaDB: `{humanize.intword(sum(await asyncio.gather(*(self.bot.db.fetchval(f'SELECT COUNT(*) FROM {t};') for t in await self.bot.db.fetch('SHOW TABLES;')))))} rows`\nCache: `{len(await self.bot.cache.keys())}` rows"
            )
            .set_footer(text=f"Page 1 / {len(self.bot.clusters)+1}")
        )
        
        for cluster in self.bot.clusters:
            embed = discord.Embed(
                color=self.bot.color,
                title=f"Cluster {cluster}"
            )
            for shard in filter(lambda si: si._parent.cluster_id == cluster, self.bot.shards.values()):
                status = "Operational" if not any((shard.is_closed(), shard.is_ws_ratelimited())) else "Non-Operational"
                uptime = shard._parent.uptime
            
                now = datetime.now(pytz.timezone("America/New_York"))
                last_ping = vile.fmtseconds(now.timestamp()-(now-timedelta(seconds=shard.latency)).timestamp()) if status == "Operational" else "N/A"
                uptime = vile.fmtseconds(now.timestamp()-uptime.timestamp()) if status == "Operational" else "N/A"
            
                embed.add_field(
                    name=f"Shard #{shard.id}",
                    value=f"Status: `{status}`\nLast ping: `{last_ping} ago`\nUptime: `{uptime}`"
                )
            
            embed.set_footer(text=f"Page {cluster+1} / {len(self.bot.clusters)+1}")
            embeds.append(embed)
            
        return await ctx.paginate(embeds)

            
async def setup(bot: vile.VileBot) -> None:
    await bot.add_cog(Developer(bot))