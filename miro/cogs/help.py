import discord
from discord.ext import commands
from typing import Union
from discord.ui import View, Button, Select
from classes import Colors, Emotes, Images

class help(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot

# --------------------------------------------------------------------------------------- Help Command

    @commands.command()
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def help(self, ctx, command=None):
        try:
            if command == None:
                embed = discord.Embed(description="\n> - **an asterisk(*) means the command has subcommands**\n > - *View Miro's commands using the menu below.*\n> - *Or view the commands on our [**` Docs `**](https://mirobot.gitbook.io/miro/commands)*", color=Colors.normal)
                embed.set_author(name="Miro's Command Menu", icon_url=f"{self.bot.user.display_avatar}", url="https://discord.gg/Mirobot")
                embed.add_field(name=f"{Emotes.reply_emote} {Emotes.support_emote} Need Extra Help?", value=f"> - Visit our [**` Support Server `**](https://discord.gg/mirobot) on how to get started\n> - Developer: [**inflating**](https://discord.com/users/129857040855072768)")
                await ctx.send(embed=embed, view=SelectView())
            else:
                cmd = self.bot.get_command(command)
                embed = discord.Embed(
                    color=0x4c5264,
                    title=f"Command: {cmd.name}",
                    description=f"{'N/A' if not cmd.description else cmd.description}")
                embed.add_field(
                    name="**Aliases**",
                    value=f"{'N/A' if not cmd.aliases else ', '.join(a for a in cmd.aliases)}",
                    inline=False
                )
                embed.add_field(
                    name="**Usage**",
                    value=f"```{ctx.clean_prefix}{cmd.usage}```",
                    inline=False
                )
                embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar)
                embed.set_thumbnail(url=self.bot.user.avatar)
                embed.set_footer(text=f"Module: {cmd.cog_name}")
                await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(e)


class Select(discord.ui.Select):
    def __init__(self):
        options=[
            discord.SelectOption(label="Main Menu", description="Go back to the main menu."),
            discord.SelectOption(label="Information", description="View Miro's Information commands."),
            discord.SelectOption(label="Configuration", description="View Miro's Configuration commands."),
            discord.SelectOption(label="Moderation", description="View Miro's Moderation commands."),
            discord.SelectOption(label="Utility", description="View Miro's Utility commands."),
            discord.SelectOption(label="Miscellaneous", description="View Miro's Miscellaneous commands."),
            discord.SelectOption(label="Fun", description="View Miro's Fun commands."),
            discord.SelectOption(label="Greeting", description="View Miro's Welcome & boost commands."),
            discord.SelectOption(label="Roleplay", description="View Miro's Roleplay commands."),
            discord.SelectOption(label="Crypto", description="View Miro's Crypto commands.")
            ]

        super().__init__(placeholder="Miro's Command Modules", max_values=1, min_values=1, options=options)
    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "Main Menu":
            e1 = discord.Embed(description="> - *View Miro's commands using the menu below.*\n> - *Or view the commands on our [**` Docs `**](https://Miro.gitbook.io/docs/)*", color=Colors.normal)
            e1.set_author(name="Miro's Command Menu", icon_url=f"{Images.Miro_pfp}", url="https://discord.gg/mirobot")
            e1.add_field(name=f"{Emotes.reply_emote} {Emotes.support_emote} Need Extra Help?", value=f"> - Visit our [**` Support Server `**](https://discord.gg/mirobot) on how to get started\n> - Developer: [**inflating**](https://discord.com/users/129857040855072768) ")
            await interaction.response.edit_message(embed=e1)
        elif self.values[0] == "Information":
            e2 = discord.Embed(title="**Information Commands**", description="""`helpsite*, invite*, ping *, uptime*, botinfo*, serverinfo*, userinfo*, upvote*, credits*, donate*, google*, btcinfo*, wolfram*, guildvanity*, inviteinfo*, channelinfo*, bans*, appinfo*`""",color=Colors.normal)
            e2.set_author(name="Miro's Command Menu", icon_url=f"{Images.Miro_pfp}", url="https://discord.gg/mirobot")
            await interaction.response.edit_message(embed=e2)
        elif self.values[0] == "Configuration":
            e3 = discord.Embed(title="Configuration Commands", description="""`skull*, auditlogs*, logschannel*, guildprefix*, autoresponder*, reactionrole*, autorole*, ignorechannel*, unignorechannel*, reminder*, chatfilter*, voicemaster*, vanity*, antinuke*, autoreact*, autoreact add, autoreact delete, autoreact list, timezone*, timezone set, timezone list`""",color=Colors.normal)
            e3.set_author(name="Miro's Command Menu", icon_url=f"{Images.Miro_pfp}", url="https://discord.gg/mirobot")
            await interaction.response.edit_message(embed=e3)
        elif self.values[0] == "Moderation":
            e4 = discord.Embed(title="**Moderation Commands**", description="""`ban*, unban*, kick*, jail*, unjail*, slowmode*, lock*, unlock*, forcenickname*, unforcenickname*, hardban*, hidechannel*, unhidechannel*, servername*, botclear*, mute*, unmute*, muted*, banmsg*, nickname*, addrole, role, nuke*, mods*, restore*, role humans, role all, role create`""",color=Colors.normal)
            e4.set_author(name="Miro's Command Menu", icon_url=f"{Images.Miro_pfp}", url="https://discord.gg/mirobot")
            await interaction.response.edit_message(embed=e4)
        elif self.values[0] == "Utility":
            e5 = discord.Embed(title="Utility Commands", description="""`av*, banner*, roles*, boosters*, image*, invites*, messages*, xbox*, firstmessage*, membercount*, hex*, createembed*, afk*, extract*, urban*, snipe*, editsnipe*, clearsnipe*, anime*, aninews*, servericon*, serverbanner*, serversplash*, youtube*, tiktok*, joinposition*, spotify*, github*, tts*, ocr*, weather*, fyp*, lilpeep*`""",color=Colors.normal)
            e5.set_author(name="Miro's Command Menu", icon_url=f"{Images.Miro_pfp}", url="https://discord.gg/mirobot")
            await interaction.response.edit_message(embed=e5)
        elif self.values[0] == "Miscellaneous":
            e6 = discord.Embed(title="Miscellaneous Commands", description="""`enlarge*, addemoji*, addmultiple*, deleteemoji*, emojiinfo*, antisetup*, settings*, joinlock*, unbanall*, whitelist*, unwhitelist*, unwhitelist*, punishment*, stickers*, emojis*, vanitycheck*, names*, lookup*`""",color=Colors.normal)
            e6.set_author(name="Miro's Command Menu", icon_url=f"{Images.Miro_pfp}", url="https://discord.gg/mirobot")
            await interaction.response.edit_message(embed=e6)
        elif self.values[0] == "Fun":
            e7 = discord.Embed(title="Fun Commands", description="""`rps*, blacktea*, tictactoe*, shiprate*, howretarded*, howgay*, howcool*, howhot*, bitchrate*, iqrate*, spotifyuser*, jerkoff*, simprate*, dice*, hack*, uselessfact*, eject*, ppsize*, coinflip*, 8ball*, meme*, lizard*, goose*, cat*, fox*, dog*, morse*, emojify*, reverse*, advice*, scrapbook*, marry*, divorce*, marriage*, adopt*, disown*, runaway*, children*`""",color=Colors.normal)
            e7.set_author(name="Miro's Command Menu", icon_url=f"{Images.Miro_pfp}", url="https://discord.gg/mirobot")
            await interaction.response.edit_message(embed=e7)
        elif self.values[0] == "Greeting":
            e8 = discord.Embed(title="Greeting & Boost Commands", description="""`welcome, welc message, welc channel, welc test, boost, boost message, boost channel, boost test`""",color=Colors.normal)
            e8.set_author(name="Miro's Command Menu", icon_url=f"{Images.Miro_pfp}", url="https://discord.gg/mirobot")
            await interaction.response.edit_message(embed=e8)
        elif self.values[0] == "Roleplay":
            e9 = discord.Embed(title="Roleplay commands", description="""`cuddle*, pat*, kiss*, feed*, cry*, laugh*, poke*, baka*, kill*, smile*`""",color=Colors.normal)
            e9.set_author(name="Miro's Command Menu", icon_url=f"{Images.Miro_pfp}", url="https://discord.gg/mirobot")
            await interaction.response.edit_message(embed=e9)
        elif self.values[0] == "Crypto":
            e10 = discord.Embed(title="Crypto commands", description="""`btc, ltc, eth, bnb, usdt, usdc, xrp, busd, sol, ada, dai, doge, ada, matic, dot, shib, trx, wbtc, xlm, bch, neo, leo, uni, cro, near, atom, algo, zec, usdd, usdn, ldo `""",color=Colors.normal)
            e10.set_author(name="Miro's Command Menu", icon_url=f"{Images.Miro_pfp}", url="https://discord.gg/mirobot")
            await interaction.response.edit_message(embed=e10)
            

class SelectView(discord.ui.View):
    def __init__(self, *, timeout = 190):
        super().__init__(timeout=timeout)
        self.add_item(Select())
        
async def setup(bot) -> None:
    await bot.add_cog(help(bot))