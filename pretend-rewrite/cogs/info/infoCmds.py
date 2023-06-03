import discord
from discord.ext import commands
import os

class infoCmds(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.command(
        help="donate us lol",
        usage="donate",
        aliases=["don", "dona"]
    )
    async def donate(self, ctx):
        embed = discord.Embed(color=self.bot.color, title="pretend donate", description=f"> **If you donate us you can get the perks from the command `;perks` or you can boost our [support server](https://discord.gg/whA2tm9yVb)**")
        embed.add_field(name="Links", value=f">>> [marian paypal](https://paypal.me/uinaffect)\n[hammer paypal](https://google.com)")
        embed.add_field(name="Server Support", value="> [boost it lol](https://discord.gg/whA2tm9yVb)")
        embed.set_thumbnail(url=self.bot.user.avatar.url)
        await ctx.reply(embed=embed)

    @commands.command(
        help="shows application info",
        usage="appinfo",
        aliases=["ai", "app", "a", "app-info"]
    )
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def appinfo(self, ctx, id: int):
        try:
            res = self.bot.session.get(f"https://discord.com/api/applications/{id}/rpc")
        except:
            return await ctx.reply("Invalid application id")

        avatar = f"https://cdn.discordapp.com/avatars/{res['id']}/{res['icon']}.png?size=1024"

        embed = discord.Embed(color=self.bot.color, title=res["name"], description=res["description"] or "No description for this application found")
        embed.add_field(
            name="general",
            value=f"**id**: {res['id']}\n**name**: {res['name']}\n**bot public**: {res['bot_public']}\n**bot require code grant**: {res['bot_require_code_grant']}",
        )
        embed.set_thumbnail(url=avatar)

        return await ctx.reply(embed=embed)
            
    @commands.command(
        help="shows the perks from the bot",
        usage="perks",
        aliases=["perk", "p", "per", "pe"]
    )
    async def perks(self, ctx):
        embed = discord.Embed(color=self.bot.color, title="pretend", description=f"> **If you donate us you can get the perks**")

        embed.add_field(name="Current Perks", value="""
        > `;appinfo` - shows application info
        > `;steal` - steal users embed for lastfm
        """)

        embed.set_thumbnail(url=self.bot.user.avatar.url)
        await ctx.reply(embed=embed)

    @commands.command(
        help="shows the credits from the bot",
        usage="credits",
        aliases=["cr", "credit", "cred", "c"]
    )
    async def credits(self, ctx):
        # here you go
        embed = discord.Embed(color=self.bot.color, title="pretend", description=f"> <@1071108000317714452>, <@1078962964662591528>, <@1006275329217794068> - lead devs")
        await ctx.reply(embed=embed)

    @commands.command(
        help="shows the information of the bot",
        usage="botinfo",
        aliases=["bi", "b", "bot-info", "bot", "info", "about"]
    )
    async def botinfo(self, ctx):
        members = 0
        for guild in self.bot.guilds:
            members += guild.member_count - 1
        embed = discord.Embed(color=self.bot.color, description=f"**pretend** its a multipurpose discord bot with so many features. you can use `;help` to see it!")
        embed.set_footer(text="pretend rewrite version 2.20.1", icon_url=self.bot.user.avatar.url)
        embed.add_field(name=f"Stats: ", value=f">>> Guilds: {len(self.bot.guilds)}\nUsers: {members}")
        system = os.name.replace('nt', 'Windows').replace('posix', "Linux")
        embed.add_field(name=f"", value=f">>> Commands: {len(self.bot.commands)}\nSystem: {system}")
        embed.set_thumbnail(url=self.bot.user.avatar.url)
        await ctx.reply(embed=embed)

    @commands.command(
        help="display informations about user",
        usage="userinfo [user]",
        aliases=["ui", "user", "uinfo", "whois", "who", "user-info"]
    )
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def userinfo(self, ctx, user: discord.User = None):
        if user is None:
            user = ctx.author

        badges = {
            "activeDeveloper": "<:ActiveDev:1103639843151564840> "
        }
        
        badges_str = ""

        if user.public_flags.active_developer:
            badges_str += badges["activeDeveloper"]

        embed = discord.Embed(
            color=self.bot.color,
            title=f"{user.name}"
        )

        embed.set_thumbnail(url=user.avatar.url or user.default_avatar.url)
        embed.add_field(
            name="general",
            value=f"**name**: {user.name}\n**bot**: {user.bot}\n**created at**: <t:{int(user.created_at.timestamp())}:F> (<t:{int(user.created_at.timestamp())}:R>)\n**avatar url**: [click here]({user.avatar.url or user.default_avatar.url})",
        )

        embed.set_author(
            name=f"{user.name} • {sorted(ctx.guild.members, key=lambda m: m.joined_at).index(user) + 1}th member",
            icon_url=user.avatar.url or user.default_avatar.url
        )


        embed.set_footer(
            text=f"{len(user.mutual_guilds)} mutual guild(s) | ID: {user.id}"
        )

        if user in ctx.guild.members:
            member = ctx.guild.get_member(user.id)
            embed.add_field(
                name="guild",
                value=f"**nick**: {member.nick}\n**joined at**: <t:{int(member.joined_at.timestamp())}:F> (<t:{int(member.joined_at.timestamp())}:R>)\n**top role**: {member.top_role.mention}\n**color**: {member.color}",
                inline=False
            )

        await ctx.reply(embed=embed)

    @commands.command(
        help="display informations about server",
        usage="serverinfo",
        aliases=["si", "server", "sinfo", "guild", "ginfo", "guildinfo"]
    )
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def serverinfo(self, ctx, guild: discord.Guild = None):
        if guild is None:
            guild = ctx.guild

        embed = discord.Embed(
            color=self.bot.color,
            title=f"{guild.name} • shard: {guild.shard_id + 1}/{self.bot.shard_count}"
        )

        embed.set_thumbnail(url=guild.icon.url or None)
        embed.add_field(
            name="general",
            value=f"**name**: {guild.name}\n**id**: {guild.id}\n**created at**: <t:{int(guild.created_at.timestamp())}:F> (<t:{int(guild.created_at.timestamp())}:R>)\n**icon url**: [click here]({guild.icon.url or None})\n**member count**: {guild.member_count}\n**boost level**: {guild.premium_tier}\n**boost count**: {guild.premium_subscription_count}",
            inline=False
        )

        await ctx.reply(embed=embed)

    @commands.command(
        help="display informations about channel",
        usage="channelinfo [channel]",
        aliases=["ci", "channel", "cinfo", "chinfo", "channel-info"]
    )
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def channelinfo(self, ctx, channel: discord.TextChannel = None):
        if channel is None:
            channel = ctx.channel

        embed = discord.Embed(
            color=self.bot.color,
            title=f"{channel.name} • shard: {channel.guild.shard_id + 1}/{self.bot.shard_count}"
        )

        embed.add_field(
            name="general",
            value=f"**name**: {channel.name}\n**id**: {channel.id}\n**created at**: <t:{int(channel.created_at.timestamp())}:F> (<t:{int(channel.created_at.timestamp())}:R>)\n**category**: {channel.category.name if channel.category else None}\n**topic**: {channel.topic if channel.topic else None}",
            inline=False
        )

        await ctx.reply(embed=embed)

    @commands.command(
        help="display informations about role",
        usage="roleinfo [role]",
        aliases=["ri", "rinfo", "role-info"]
    )
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def roleinfo(self, ctx, role: discord.Role = None):
        if role is None:
            role = ctx.guild.default_role

        embed = discord.Embed(
            color=self.bot.color,
            title=f"{role.name} • shard: {role.guild.shard_id + 1}/{self.bot.shard_count}"
        )

        embed.add_field(
            name="general",
            value=f"**name**: {role.name}\n**id**: {role.id}\n**created at**: <t:{int(role.created_at.timestamp())}:F> (<t:{int(role.created_at.timestamp())}:R>)\n**color**: {role.color}\n**mentionable**: {role.mentionable}\n**hoisted**: {role.hoist}\n**position**: {role.position}",
            inline=False
        )


        if role.managed:
            embed.add_field(
                name="managed",
                value="yes"
            )
        if role.members:
            embed.add_field(
                name="members ({})".format(len(role.members)),
                value=", ".join([m.mention for m in role.members[:10]]) + ("..." if len(role.members) > 10 else ""),
                inline=False
            )

        embed.set_thumbnail(url=getattr(
            role.icon, "url", None
        ))

        await ctx.reply(embed=embed)

async def setup(bot):
    await bot.add_cog(infoCmds(bot))