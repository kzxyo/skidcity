import discord, aiosqlite ; from discord.ext import commands ; from .utils.util import Emojis

class reactionrole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(aliases=['rr'])
    async def reactionrole(self, ctx):
        if ctx.subcommand_passed is not None:
            return
        embed = discord.Embed(color=0xf7f9f8, title="reaction roles", description="have our bot give a user a role when they react to a message")
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar.url)
        embed.add_field(name="category", value="config")
        embed.add_field(name="commands", value=">>> reactionrole add\nreactionrole remove\nreactionrole list", inline=False)
        embed.add_field(name="usage", value=f"```,reactionrole <subcommand> [roleid] [messageid] <emoji>```", inline=False)
        embed.set_footer(text=f"aliases: rr")
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        await ctx.reply(embed=embed, mention_author=False)
        return
    @reactionrole.command()
    async def add(self, ctx, role_id: int, message_id: int, emoji: str):
        async with aiosqlite.connect('database.db') as db:
            await db.execute('CREATE TABLE IF NOT EXISTS reaction_roles (role_id INTEGER, message_id INTEGER, emoji TEXT, PRIMARY KEY (role_id, message_id, emoji))')
            await db.commit()
            await db.execute('INSERT INTO reaction_roles (role_id, message_id, emoji) VALUES (?, ?, ?)', (role_id, message_id, emoji))
            await db.commit()
        message = await ctx.channel.fetch_message(message_id)
        await message.add_reaction(emoji)
        e = discord.Embed(
            description=f"{Emojis.check} Reaction role added successfully",
            color=0xf7f9f8
        )
        await ctx.send(embed=e, mention_author=False)

    @reactionrole.command()
    async def remove(self, ctx, role: discord.Role, message: discord.Message, emoji: str):
        async with aiosqlite.connect('database.db') as db:
            result = await db.execute('SELECT * FROM reaction_roles WHERE role_id = ? AND message_id = ? AND emoji = ?', (role.id, message.id, emoji))
            row = await result.fetchone()
            if row is None:
                # If not found, send an error message and return
                e = discord.Embed(
                    description=f"{Emojis.warn} Invalid roleid, messageid, or emoji",
                    color=0xf7f9f8
                )
                await ctx.send(embed=e, mention_author=False)
                return
            await db.execute('DELETE FROM reaction_roles WHERE role_id = ? AND message_id = ? AND emoji = ?', (role.id, message.id, emoji))
            await db.commit()
        await message.clear_reaction(emoji)
        e = discord.Embed(
            description=f"{Emojis.check} Reaction role removed successfully",
            color=0xf7f9f8
        )
        await ctx.send(embed=e, mention_author=False)  

    @reactionrole.command()
    async def list(self, ctx):
        async with aiosqlite.connect('database.db') as db:
            cursor = await db.execute('SELECT role_id, message_id, emoji FROM reaction_roles')
            rows = await cursor.fetchall()
        embed = discord.Embed(title='reaction role list', color=0xf7f9f8)
        for row in rows:
            role = ctx.guild.get_role(row[0])
            message = await ctx.channel.fetch_message(row[1])
            embed.add_field(name=f'{message.id} - {role.name}', value=f'React with {row[2]} to get the {role.name} role', inline=False)
        await ctx.send(embed=embed)  

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        async with aiosqlite.connect('database.db') as db:
            cursor = await db.execute('SELECT role_id FROM reaction_roles WHERE message_id = ? AND emoji = ?', (payload.message_id, str(payload.emoji)))
            row = await cursor.fetchone()
            if row is not None:
                guild = await self.bot.fetch_guild(payload.guild_id)
                member = await guild.fetch_member(payload.user_id)
                role = guild.get_role(row[0])
                if role is not None:
                    await member.add_roles(role)
    
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        async with aiosqlite.connect('database.db') as db:
            cursor = await db.execute('SELECT role_id FROM reaction_roles WHERE message_id = ? AND emoji = ?', (payload.message_id, str(payload.emoji)))
            row = await cursor.fetchone()
            if row is not None:
                guild = await self.bot.fetch_guild(payload.guild_id)
                member = await guild.fetch_member(payload.user_id)
                role = guild.get_role(row[0])
                if role is not None:
                    await member.remove_roles(role)

async def setup(bot):
    await bot.add_cog(reactionrole(bot))