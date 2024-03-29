import discord, time
from discord.ext import commands
from modules.func import member
from modules.errors import *

class emoji(commands.Cog, description = "see emoji commands"):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(extras={"Category": "Emoji"}, usage="steal **!emojis", help="Steal emojis from other guilds", aliases=["addemoji", "addemojis"])
    @member.has_perm("manage_emojis")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def steal(self, ctx, *emojis):
        if not emojis:
            raise Var("emojis")
        await ctx.typing()
        err = []
        suc = []
        for emo in emojis:
            try:
                e = await commands.PartialEmojiConverter().convert(ctx, emo)

                img = await e.read()
                em = await ctx.guild.create_custom_emoji(image=img, name=e.name)
                suc.append(em)
                time.sleep(1.5)
            except:
                err.append(e)
        if suc and not err:
            msg = f"added {', '.join(str(e) for e in suc)} ({len(ctx.guild.emojis)}/{ctx.guild.emoji_limit} emojis)"
            await ctx.succes(msg)
        if err and suc:
            msg = f"added {', '.join(str(e) for e in suc)} and {len(err)} emojis can't be added"
            await ctx.succes(msg)
        elif err and not suc:
            msg = f"{len(err)} emojis can't be added"
            await ctx.error(msg)
            
async def setup(bot):
    await bot.add_cog(emoji(bot))
