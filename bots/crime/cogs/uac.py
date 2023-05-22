import discord, aiosqlite ; from discord import Embed ; from discord.ext.commands import Cog, command, cooldown, BucketType, AutoShardedBot as Bot, has_permissions, Group
from .utils.util import Emojis
from cogs.utilevents import blacklist, noperms, commandhelp

class user(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot 

    @command(help="creates category", description="utility", usage="[categoryname]", aliases=['categorycreate', 'makecategory', 'categorymake'])
    @blacklist()
    async def createcategory(self, ctx, category_name):
        if not ctx.author.guild_permissions.manage_channels:
            await noperms(self, ctx, "manage_channels")
            return
        existing_category = discord.utils.get(ctx.guild.categories, name=category_name)
        if existing_category:
            e = Embed(
               description=f"{Emojis.check} the category **{category_name}** already exists.",
               color=0xf7f9f8
            )
            await ctx.reply(embed=e, mention_author=False)
        else:
            await ctx.guild.create_category(category_name)
            e = Embed(
               description=f"{Emojis.check} the category **{category_name}** has been created.",
               color=0xf7f9f8
            )      
            await ctx.reply(embed=e, mention_author=False)

    @command(help="deletes category", description="utility", usage="[categoryname]", aliases=['categorydelete', 'removecategory', 'removecreate'])
    @blacklist()
    async def deletecategory(self, ctx, category_name):
        if not ctx.author.guild_permissions.manage_channels:
            await noperms(self, ctx, "manage_channels")
            return
        category = discord.utils.get(ctx.guild.categories, name=category_name)
        if not category:
            e = Embed(
               description=f"{Emojis.check} the category **{category_name}** does not exist.",
               color=0xf7f9f8
            )
            await ctx.reply(embed=e, mention_author=False)
        else:
            await category.delete(reason=f"Category deleted by {ctx.author}")
            e = Embed(
               description=f"{Emojis.check} the category **{category_name}** has been deleted.",
               color=0xf7f9f8
            )
            await ctx.reply(embed=e, mention_author=False)

    @command(help="creates a channel", description="utility", usage="[channelname]", aliases=['channelcreate', 'makechannel', 'channelmake'])
    @cooldown(1, 4, BucketType.user)
    @blacklist()
    async def createchannel(self, ctx, channel_name: str):
        if channel_name is None:
            embed = discord.Embed(color=0xf7f9f8, title="text channel", description="create or delete a text channel")
            embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar.url)
            embed.add_field(name="category", value="utility")
            embed.add_field(name="commands", value=",createchannel\n,deletechannel", line=False)
            embed.add_field(name="usage", value=f"```,createchannel .gg/runs```", inline=False)
            embed.add_field(name=f"aliases", value= "channelcreate, makechannel, channelmake\nchanneldelete, removechannel, channelremove")
            await ctx.reply(embed=embed, mention_author=False)            
            return
        if not ctx.author.guild_permissions.manage_channels:
            await noperms(self, ctx, "manage_channels")
            return
        guild = ctx.guild
        echnl = discord.utils.get(guild.channels, name=channel_name)
        if not echnl:
            await guild.create_text_channel(channel_name)
            await ctx.message.delete()
            e = Embed(description=f'{Emojis.check} The **{channel_name}** channel has been created.')
            await ctx.send(embed = e)
        else:
            e = Embed(description=f'{Emojis.warn} That channel already exists.')
            await ctx.reply(embed = e, mention_author=False)   

    @command(help="delete channel", description="utility", usage="[channel]", aliases=['channeldelete', 'removechannel', 'channelremove'])
    @cooldown(1, 4, BucketType.user)
    @blacklist()
    async def deletechannel(self, ctx, channel: discord.TextChannel):
        if channel is None:
            embed = discord.Embed(color=0xf7f9f8, title="text channel", description="create or delete a text channel")
            embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar.url)
            embed.add_field(name="category", value="utility")
            embed.add_field(name="commands", value=",createchannel\n,deletechannel", inline=False)
            embed.add_field(name="usage", value=f"```,createchannel .gg/runs```", inline=False)
            embed.add_field(name=f"aliases", value= "channelcreate, makechannel, channelmake\nchanneldelete, removechannel, channelremove")
            await ctx.reply(embed=embed, mention_author=False)            
            return
        if not ctx.author.guild_permissions.manage_channels:
            await noperms(self, ctx, "manage_channels")
            return
        guild = ctx.guild
        echnl = discord.utils.get(guild.channels)
        if echnl:
            await channel.delete()
            await ctx.message.delete()
            e = Embed(description=f'{Emojis.check} The **{channel}** channel has been deleted.')
            await ctx.send(embed = e)

async def setup(bot):
    await bot.add_cog(user(bot))