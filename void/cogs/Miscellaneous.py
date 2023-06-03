from discord.ext import commands
import discord
from deep_translator import GoogleTranslator
from rivalapi.rivalapi import RivalAPI
from utils.paginator import Paginator
import re
from utils.embed import to_object, embed_replacement
from typing import Union

color = 0x2b2d31

class Miscellaneous(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.rival=RivalAPI('63176c61-4622-4f42-8eaf-76f93f7841a3')

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} cog has been loaded\n-----")

    @commands.command(
            name='invite',
            description='View the bot invite',
            usage='Syntax: invite',
            aliases=['inv']
        )
    async def invite(self, ctx):
        await ctx.typing()

        inv = 'https://discord.com/api/oauth2/authorize?client_id=1075226332935503913&permissions=8&scope=bot'
        await ctx.success(f'Click **[here]({inv})** to invite **{self.bot.user.name}**')

    @commands.command(
        name='afk',
        description='Set you away message for when you\'re mentioned',
        brief='status',
        usage='Syntax: <status>',
        aliases=['sleep', 'away']
    )
    async def afk(self, ctx, *, status: str = 'AFK'):
        await ctx.typing()

        timestamp = int(round(discord.utils.utcnow().timestamp()))
        await self.bot.db.execute('INSERT INTO afk (author, status, timestamp) VALUES ($1, $2, $3)', ctx.author.id, status, timestamp)
        await ctx.success(f'You\'re now **AFK** with the status: **{status}**')

    @commands.command(
        name='translate',
        description='Transalte any text to a different language',
        brief='language, text',
        usage=
        'Syntax: (language) (text)\n'
        'Example: spanish How are you?'
    )
    async def translate(self, ctx, language: str, *, text: str):
        await ctx.typing()

        trans=GoogleTranslator(
                source='auto',
                target=language
            )
        await ctx.success(trans.translate(text=text))
    
    @commands.command(
        name='image',
        description='Search Google for an image',
        brief='query',
        usage=
        'Syntax: image (query)\n'
        'Example: J. Cole',
        aliases=['img', 'i', 'im']
    )
    async def image(self, ctx, *, query):
        await ctx.typing()

        data = await self.rival.google_images(query=query, safe=True)
        embeds = []
        for pagenum,i in enumerate(data.results,start=1):
            total=len(data.results)
            embeds.append(discord.Embed(
                color=color,
                title=f'{query}',
                description=f"[{i.title}]({i.domain})",url=i.source).set_image(url=i.url)
                .set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar)
                .set_footer(text=f'Page {pagenum}/{total}')
                )
        pag = Paginator(self.bot, embeds, ctx, invoker=ctx.author.id)
        pag.add_button('prev', emoji='<:void_previous:1082283002207424572>')
        pag.add_button('goto', emoji='<:void_goto:1082282999187517490>')
        pag.add_button('next', emoji='<:void_next:1082283004321341511>')
        pag.add_button('delete', emoji='<:void_cross:1082283006649188435>')
        await pag.start()
            
    # @commands.command(
    #     name='lookup',
    #     description='Look up recently changed usernames',
    #     brief='discriminator',
    #     usage=
    #     'Syntax: <discriminator>\n'
    #     'Example: 9999',
    #     aliases=['tags']
    # )
    # async def lookup(self, ctx, lookup = None):
    #     await ctx.typing()

    #     lookup = '0001' if lookup is None else lookup
    #     tags = await self.rival.tags(discriminator=lookup)
    #     if tags is None:
    #         await ctx.success(f'> No recent **{lookup}** tags')
    #     embeds = []
    #     ret = []
    #     num = 0
    #     pagenum = 0
    #     for t in tags:
    #         t=t.replace("**","")
    #         num += 1
    #         ret.append(f'**{num}.** {t}')
    #         pages = [p for p in discord.utils.as_chunks(ret, 10)]
    #     for page in pages:
    #         pagenum += 1
    #         embeds.append(discord.Embed(
    #             color=color,
    #             title=f'Recently available {lookup} tags',
    #             description="\n".join(page))
    #             .set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar)
    #             .set_footer(text=f'Page {pagenum}/{len(pages)}')
    #             )
    #     if len(embeds) == 1:
    #         return await ctx.send(embed=embeds[0])
    #     else:
    #         pag = Paginator(self.bot, embeds, ctx, invoker=ctx.author.id)
    #         pag.add_button('prev', emoji='<:void_previous:1082283002207424572>')
    #         pag.add_button('goto', emoji='<:void_goto:1082282999187517490>')
    #         pag.add_button('next', emoji='<:void_next:1082283004321341511>')
    #         pag.add_button('delete', emoji='<:void_cross:1082283006649188435>')
    #         await pag.start()

    @commands.command(
        name='createembed',
        description='Create a custom embed',
        brief='code',
        usage=
        'Syntax: (embed code)\n'
        'Example: {title: void}$v{description: into the void}',
        aliases=['customembed', 'ce']
    )
    async def createembed(self, ctx, *, embed = None):
        await ctx.typing()

        if not embed: return await ctx.send_help(ctx.command)
        result = await to_object(embed)
        embed = result['embed']
        if embed:
            if embed.title:
                embed.title = await embed_replacement(ctx.author, embed.title)
            if embed.description:
                embed.description = await embed_replacement(ctx.author, embed.description)
            if embed.footer:
                if embed.footer.text and embed.footer.icon_url:
                    embed.set_footer(text=await embed_replacement(ctx.author, embed.footer.text), icon_url=await embed_replacement(ctx.author, embed.footer.icon_url))
                elif embed.footer.text:
                    embed.set_footer(text=await embed_replacement(ctx.author, embed.footer.text))
                elif embed.footer.icon_url:
                    embed.set_footer(icon_url=await embed_replacement(ctx.author, embed.footer.icon_url))
            if embed.author:
                if embed.author.name and embed.author.icon_url:
                    embed.set_author(name=await embed_replacement(ctx.author, embed.author.name), icon_url=await embed_replacement(ctx.author, embed.author.icon_url))
                elif embed.author.name:
                    embed.set_author(name=await embed_replacement(ctx.author, embed.author.name))
                elif embed.author.icon_url:
                    embed.set_author(icon_url=await embed_replacement(ctx.author, embed.author.icon_url))
            if embed.fields:
                for field in embed.fields:
                    if field.name:
                        embed.set_field_at(index=embed.fields.index(field), name=await embed_replacement(ctx.author, field.name), value=await embed_replacement(ctx.author, field.value), inline=field.inline)
            if embed.image:
                embed.set_image(url=await embed_replacement(ctx.author, embed.image.url))
            if embed.thumbnail:
                embed.set_thumbnail(url=await embed_replacement(ctx.author, embed.thumbnail.url))
        content = result['content']
        if content:
            content = await embed_replacement(ctx.author, content)
        msg = await ctx.send(content=content, embed=embed, view=result['view'], files=result['files'], delete_after=result['delete_after'], allowed_mentions=discord.AllowedMentions(users=True, everyone=False))

    @commands.command(
        name='snipe',
        description='View deleted messages',
        brief='index',
        usage=
        'Syntax: <index>\n'
        'Example: 2',
        aliases=['sn', 's']
    )
    async def snipe(self, ctx, page: int = 1):
        from datetime import datetime
        await ctx.typing()

        messages_per_page = 1 # Change this number to adjust the number of messages per page
        offset = (page - 1) * messages_per_page
        count = await self.bot.db.fetchval("SELECT COUNT(*) FROM snipe WHERE channel_id = $1", ctx.channel.id)
        total_pages = (count + messages_per_page - 1) // messages_per_page
        data = await self.bot.db.fetch(
            "SELECT * FROM snipe WHERE channel_id = $1 ORDER BY id DESC LIMIT $2 OFFSET $3",
            ctx.channel.id, messages_per_page, offset
        )
        if not data:
            return await ctx.success("No deleted messages found")
        if data:
            author = await self.bot.fetch_user(data[0][3])
            content = data[0][4]
            e = discord.Embed(
                timestamp=datetime.utcnow(),
                color=color,
                description=content
            )
            e.set_author(name=f'{author.name}', icon_url=author.display_avatar)
            e.set_footer(text=f"Page {page}/{total_pages}")
            if data[0][5]: # If there is an attachment in the message
                if data[0][6] in ["image", "video", "gif"]: # If the attachment is an image, video, or gif
                    e.set_image(url=data[0][5])
                elif data[0][6] == "audio": # If the attachment is audio
                    e.add_field(name="Attachment", value=f"[{data[0][5]}]({data[0][5]})")
                else: # If the attachment is another type
                    e.add_field(name="Attachment", value=data[0][5])
            await ctx.send(embed=e)

    @commands.command(
        name='editsnipe',
        description='View edited messages',
        brief='index',
        usage=
        'Syntax: <index>\n'
        'Example: 2',
        aliases=['esnipe', 'es', 'eh']
    )
    async def editsnipe(self, ctx, page: int = 1):
        from datetime import datetime
        await ctx.typing()

        messages_per_page = 1 # Change this number to adjust the number of messages per page
        offset = (page - 1) * messages_per_page
        count = await self.bot.db.fetchval("SELECT COUNT(*) FROM editsnipe WHERE channel_id = $1", ctx.channel.id)
        total_pages = (count + messages_per_page - 1) // messages_per_page
        data = await self.bot.db.fetch(
            "SELECT * FROM editsnipe WHERE channel_id = $1 ORDER BY id DESC LIMIT $2 OFFSET $3",
            ctx.channel.id, messages_per_page, offset
        )
        if not data:
            return await ctx.success("No edited messages found")
        author = await self.bot.fetch_user(data[0][3])
        content = data[0][4]
        e = discord.Embed(
            timestamp=datetime.utcnow(),
            color=color,
            description=content
        )
        e.set_author(name=f'{author.name}', icon_url=author.display_avatar)
        e.set_footer(text=f"Page {page}/{total_pages}")
        if data[0][5]: # If there is an attachment in the message
            if data[0][6] in ["image", "video", "gif"]: # If the attachment is an image, video, or gif
                e.set_image(url=data[0][5])
            elif data[0][6] == "audio": # If the attachment is audio
                e.add_field(name="Attachment", value=f"[{data[0][5]}]({data[0][5]})")
            else: # If the attachment is another type
                e.add_field(name="Attachment", value=data[0][5])
        await ctx.send(embed=e)

    @commands.command(
        name='reactionsnipe',
        description='View removed reactions',
        brief='message, index',
        usage=
        'Syntax: (message) <index>\n'
        'Example: 1080672479426646136 2',
        aliases=['rsnipe', 'rs', 'rh']
    )
    async def reactionsnipe(self, ctx, message_id: int, page: int = 1):
        from datetime import datetime
        await ctx.typing()

        messages_per_page = 1
        offset = (page - 1) * messages_per_page
        count = await self.bot.db.fetchval("SELECT COUNT(*) FROM reactionsnipe WHERE message_id = $1", message_id)
        total_pages = (count + messages_per_page - 1) // messages_per_page
        data = await self.bot.db.fetch(
            "SELECT * FROM reactionsnipe WHERE message_id = $1 ORDER BY id DESC LIMIT $2 OFFSET $3",
            message_id, messages_per_page, offset
        )
        if not data:
            return await ctx.success("No removed reactions found")
        removed_reactions_str = ""
        author = await self.bot.fetch_user(data[0][4])
        reaction = data[0][5]
        channel_id = data[0][2]
        channel = self.bot.get_channel(channel_id)
        if reaction.startswith("<") and reaction.endswith(">"):  # Custom emote
            emoji_id = int(reaction.split(":")[2][:-1])
            emoji = await ctx.guild.fetch_emoji(emoji_id)
        else:
            emoji = reaction
        message_url = f"https://discord.com/channels/{ctx.guild.id}/{channel.id}/{message_id}"
        removed_reactions_str += f"[{emoji}]({message_url})\n"
        e = discord.Embed(
            description=removed_reactions_str,
            color=color,
            timestamp=datetime.utcnow()
        )
        e.set_author(name=f'{author.name}', icon_url=author.display_avatar)
        e.set_footer(text=f"Page {page}/{total_pages}")
        await ctx.send(embed=e)

    @commands.command(
        name='clearsnipes',
        description='Clear deleted channel messages from the database',
        usage='Syntax: ',
        aliases=['clearsnipe', 'cs']
    )
    @commands.has_permissions(manage_messages=True)
    async def clearsnipes(self, ctx):
        await self.bot.db.execute('DELETE FROM snipe WHERE guild_id = $1', ctx.guild.id)
        await self.bot.db.execute('DELETE FROM editsnipe WHERE guild_id = $1', ctx.guild.id)
        await self.bot.db.execute('DELETE FROM reactionsnipe WHERE guild_id = $1', ctx.guild.id)
        await ctx.message.add_reaction('👍🏾')

    @commands.command(
        name='names',
        description='Display a members name history',
        brief='user',
        usage=
        'Syntax: <user>\n'
        'Example: @court#9000'
    )
    async def names(self, ctx, member: Union[discord.Member, discord.User] = None):
        member = ctx.author if member is None else member
        await ctx.typing()

        data = await self.bot.db.fetch('SELECT username, discriminator, timestamp FROM names WHERE user_id = $1 ORDER BY timestamp DESC', member.id)
        if not data:
            await ctx.success(f"No previously recorded names for {member.mention}")
        embeds = []
        ret = []
        num = 0
        pagenum = 0
        for row in data:
            num += 1
            ret.append(f'**{num}.** {row["username"]}#{row["discriminator"]} - {discord.utils.format_dt(row["timestamp"], style="R")}')
        pages = [p for p in discord.utils.as_chunks(ret, 10)]
        for page in pages:
            pagenum += 1
            embeds.append(discord.Embed(
                title=f"{member.name}'s previous names",
                color=color, 
                description="\n".join(page))
                .set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar)
                .set_footer(text=f"Page {pagenum}/{len(pages)}")
                )
        if len(embeds) == 1:
            return await ctx.send(embed=embeds[0])
        else:
            pag = Paginator(self.bot, embeds, ctx, invoker=ctx.author.id)
            pag.add_button("prev", emoji="<:void_previous:1082283002207424572>")
            pag.add_button("goto", emoji="<:void_goto:1082282999187517490>")
            pag.add_button("next", emoji="<:void_next:1082283004321341511>")
            pag.add_button("delete", emoji="<:void_cross:1082283006649188435>")
            await pag.start()

    @commands.command(
        name='clearnames',
        description='Clear your name history',
        usage='Syntax: ',
        aliases=['cn']
    )
    async def clearnames(self, ctx):
        await ctx.typing()
        data = await self.bot.db.fetch('SELECT * FROM names WHERE user_id = $1', ctx.author.id)
        if data:
            await self.bot.db.execute('DELETE FROM names WHERE user_id = $1', ctx.author.id)
            await ctx.success('Cleared your name history')
        if not data:
            await ctx.success(f"No previously recorded names for {ctx.author.mention}")

async def setup(bot):
    await bot.add_cog(Miscellaneous(bot))