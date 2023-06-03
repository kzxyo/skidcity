import discord
from discord.ext import commands
import asyncpg
import prettytable

class db(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(help="N/A", usage="db", hidden=True, invoke_without_command=True)
    @commands.is_owner()
    async def db(self, ctx):
        # display all subcommands in tbale prettytable
        table = prettytable.PrettyTable()
        table.field_names = ["Subcommand", "Description", "Usage"]
        # automaticcly find all subcommands
        for command in self.walk_commands():
            table.add_row([command.name, command.help, command.usage])
        await ctx.reply(f"```bf\n{table}```")

    @db.command(help="N/A", usage="db tables", hidden=True)
    @commands.is_owner()
    async def tables(self, ctx):
        table = prettytable.PrettyTable()
        table.field_names = ["Table Name", 'Size', 'Rows']
        async with self.bot.db.acquire() as connection:
            # display all tables using simple method
            tables = await connection.fetch("SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname != 'pg_catalog' AND schemaname != 'information_schema';")
            
            # get tables sizes and rows
            for table_name in tables:
                size = await connection.fetchval(f"SELECT pg_size_pretty(pg_total_relation_size('{table_name[0]}'));")
                rows = await connection.fetchval(f"SELECT COUNT(*) FROM {table_name[0]};")
                # display columns names
                columns = await connection.fetchval(f"SELECT array_to_string(ARRAY(SELECT column_name::text FROM information_schema.columns WHERE table_name = '{table_name[0]}'), ', ');")
                table.add_row([table_name[0], size, rows])
        await ctx.reply(f"```bf\n{table}```")

    # display table
    @db.command(help="N/A", usage="db display <table name>", hidden=True, aliases=["show"])
    @commands.is_owner()
    async def display(self, ctx, table_name: str):
        # display table in prettytable
        table = prettytable.PrettyTable()

        async with self.bot.db.acquire() as connection:
            # get columns names
            columns = await connection.fetchval(f"SELECT array_to_string(ARRAY(SELECT column_name::text FROM information_schema.columns WHERE table_name = '{table_name}'), ', ');")
            table.field_names = columns.split(", ")

            # get all rows
            rows = await connection.fetch(f"SELECT * FROM {table_name};")
            for row in rows:
                table.add_row(row)

        await ctx.reply(f"```fix\n{table}```")

    # rename table command
    @db.command(help="N/A", usage="db rename <old table name> <new table name>", hidden=True, aliases=["ren"])
    @commands.is_owner()
    async def rename(self, ctx, old_table_name: str, new_table_name: str):
        async with self.bot.db.acquire() as connection:
            await connection.execute(f"ALTER TABLE {old_table_name} RENAME TO {new_table_name};")
        await ctx.reply(f"Renamed table **`{old_table_name}`** to **`{new_table_name}`**")

    # delete table command
    @db.command(help="N/A", usage="db delete <table name>", hidden=True, aliases=["del", "remove", "rm", 'drop'])
    @commands.is_owner()
    async def delete(self, ctx, table_name: str):
        async with self.bot.db.acquire() as connection:
            await connection.execute(f"DROP TABLE {table_name};")
        await ctx.reply(f"Deleted table **`{table_name}`**")

    # create table command
    @db.command(help="N/A", usage="db create <table name> <columns>", hidden=True, aliases=["add"])
    @commands.is_owner()
    async def create(self, ctx, table_name: str, *, column: str):
        async with self.bot.db.acquire() as connection:
            try:
                await connection.execute(f"CREATE TABLE {table_name} ({column});")
            except asyncpg.exceptions.DuplicateTableError:
                await ctx.reply(f"Table **`{table_name}`** already exists")
                return
            except asyncpg.exceptions.InvalidTableDefinitionError:
                await ctx.reply(f"Invalid table definition")
                return
        await ctx.reply(f"Created table **`{table_name}`**")
    
    @db.command(help="execute sql commands", usage="db execute <sql query>", hidden=True, aliases=['exec'])
    @commands.is_owner()
    async def execute(self, ctx: commands.Context, *, query: str): 
     try: 
       await self.bot.db.execute(query)
       return await ctx.message.add_reaction("<:check:1103620514343297044>")
     except: return await ctx.reply("Invalid sql command provided")     

async def setup(bot):
    await bot.add_cog(db(bot))