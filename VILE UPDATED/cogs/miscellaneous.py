import discord, typing, uwupy, time, arrow, psutil, copy, aiohttp, pytesseract, io, unicodedata, random, psutil, asyncio
from bs4 import BeautifulSoup
from datetime import datetime
from collections import deque
from typing import Optional, Union
from PIL import Image
from deep_translator import GoogleTranslator
from utilities import utils
from utilities.baseclass import Vile
from utilities.paginator import text_creator
from utilities.context import Context
from utilities.rtfm import RTFM
from utilities.utils import aiter
from discord.ext import commands


class Miscellaneous(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot


    @commands.command(
        name='createembed',
        aliases=['ce', 'embed'],
        description='create an embed using the custom format',
        brief='embed <code>',
        help='embed {embed}{description: hi}$v{color: #2f3136}\n<:vile_reply:997487959093825646> **embed builder:** https://vilebot.xyz/embed\n<:vile_reply:997487959093825646> **variables:** https://vilebot.xyz/variables'
    )
    async def createembed(self, ctx: Context, *, code: str):
        
        try:
            return await ctx.send(**await utils.to_object(await utils.embed_replacement(ctx.author, code)))
        except:
            return await ctx.send_error('**something went wrong**, please remake your code using [**this**](https://vilebot.xyz/embed)')


    @commands.command(
        name='editembed',
        aliases=['ec'],
        description='edit an embed you created using the custom format',
        brief='editembed <message> <code>',
        help='editembed 1062232407622823986 {embed}{description: hi}$v{color: #2f3136}\n<:vile_reply:997487959093825646> **embed builder:** https://vilebot.xyz/embed\n<:vile_reply:997487959093825646> **variables:** https://vilebot.xyz/variables'
    )
    async def editembed(self, ctx: Context, message: discord.Message, *, code: str):

        if message.author != ctx.guild.me:
            return await ctx.send_error('please provide a **valid** message sent by me')

        code = await utils.to_object(await utils.embed_replacement(ctx.author, code))
        code.pop('files')

        await message.edit(**code)
        return await ctx.send_success('successfully **edited** that message with the new code')


    @commands.command(
        name='copyembed',
        aliases=['embedcode'],
        description='get the code of an embed',
        brief='copyembed <message or reply>',
        help='copyembed 1047076267838676992'
    )
    async def copyembed(self, ctx, message: Optional[discord.Message] = None, extra: str = None):
        
        if message is None:
            if ctx.message.reference is None:
                return await ctx.send_help()

            message = ctx.message.reference.resolved
            
        if not message.embeds:
            return
        
        for embed in message.embeds:
            code = '{embed}'
            if embed.description:
                code += '{description: '+embed.description+'}'
            
            if embed.title:
                code += '$v{title: '+embed.title+'}'
            
            if embed.footer:
                x = ''
                if embed.footer.text:
                    x += embed.footer.text
                if embed.footer.icon_url:
                    x += f' && icon: {embed.footer.icon_url}'
                code += '$v{footer: '+x+'}'
            
            if embed.thumbnail:
                code += '$v{thumbnail: '+embed.thumbnail.url+'}'
            
            if embed.image:
                code += '$v{image: '+embed.image.url+'}'
            
            if embed.fields:
                for field in embed.fields:
                    x = ''
                    n = field.name
                    v = field.value
                    i = field.inline
                    x += f'{n} && value: {v} && inline: {"true" if i else "false"}'
                    code += '$v{field: '+x+'}'
                
            if embed.author:
                x = ''
                n = embed.author.name
                i = embed.author.icon_url
                u = embed.author.url
                x += n
                if i:
                    x += f' && icon: {i}'
                if u: 
                    x += f' && url: {u}'
                code += '$v{author: '+x+'}'
                
            if embed.timestamp:
                code += '$v{timestamp: true}'
            
            if message.components:
                comp = message.components[0]
                if isinstance(comp, discord.ui.View):
                    for button in comp.children:
                        if isinstance(button, discord.Button):
                            if button.style == discord.ButtonStyle.link:
                                x = ''
                                l = button.label
                                u = button.url
                                x += f'{l} && link: {u}'
                                code += '$v{label: '+x+'}'
                        
            if embed.color:
                if embed.color.value == 0:
                    code += '$v{color: #000000}'
                else:
                    c = hex(embed.color.value).replace('0x', '')
                    code += '$v{color: #'+c+'}'
                
            code += '$v'

            if extra == '--mobile':
                return await ctx.reply(code)

            return await ctx.reply(embed=discord.Embed(color=self.bot.color, description=f'```{code}```'))


    @commands.command(
        name='steal',
        aliases=['stealemoji', 'stealemote', 'emojiadd', 'add'],
        description='steal the provided emoji',
        brief='steal <emoji> [name]',
        help='steal :50DollaLemonade: jitTrippin',
        extras={'permissions': 'manage emojis'}
    )
    @commands.has_permissions(manage_emojis=True)
    @commands.bot_has_permissions(manage_emojis=True)
    async def steal(self, ctx: Context, emoji: Union[discord.PartialEmoji, discord.Emoji], name: Optional[str] = None):

        try:
            created_emoji = await ctx.guild.create_custom_emoji(
                name=name or emoji.name,
                image=await emoji.read(),
                reason=f'steal: used by {ctx.author}'
            )
        except:
            return await ctx.send_error('cannot add more emojis to this server')

        return await ctx.send_success(f'successfully **stole** {created_emoji}')


    @commands.command(
        name='enlarge',
        aliases=['e', 'jumbo'],
        description='enlarge the provided emoji',
        brief='enlarge <emoji>',
        help='enlarge :50DollaLemonade:'
    )
    async def enlarge(self, ctx: Context, emoji: Union[discord.Emoji, discord.PartialEmoji, str]):
        
        if isinstance(emoji, (discord.Emoji, discord.PartialEmoji)):
            return await ctx.reply(file=await emoji.to_file())

        async with ctx.handle_response():
            try:
                return await ctx.reply(
                    file=await utils.file(
                        f"https://em-content.zobj.net/thumbs/240/twitter/322/{'-'.join(unicodedata.name(emoji).lower().split())}_{ord(emoji):x}.png", 
                        f'{unicodedata.name(emoji)}.png'
                    )
                )
            except:
                return await ctx.send_error('please provide a **valid** emoji')


    @commands.command(
        name='stealmultiple',
        aliases=['stealemojis', 'stealemotes', 'emojisadd', 'addmultiple'],
        description='steal the provided emoji',
        brief='stealmultiple <emojis>',
        help='stealmultiple :50DollaLemonade: :b_kirbydance:',
        extras={'permissions': 'manage emojis'}
    )
    @commands.has_permissions(manage_emojis=True)
    @commands.bot_has_permissions(manage_emojis=True)
    async def stealmultiple(self, ctx: Context, *emojis: Union[discord.PartialEmoji, discord.Emoji]):

        created_emojis = 0
        for emoji in emojis:
            try:
                await ctx.guild.create_custom_emoji(
                    name=emoji.name, 
                    image=await emoji.read(), 
                    reason=f'stealmultiple: used by {ctx.author}'
                )
                created_emojis += 1
            except:
                return await ctx.send_success(f'successfully **stole** {created_emojis} emojis; unable to add more')

        if created_emojis == 0:
            return await ctx.send_help()

        return await ctx.send_success(f'successfully **stole** {created_emojis} emojis')

    
    @commands.command(
        name='snipe',
        aliases=['s'],
        description='snipe a recently deleted message'
    )
    async def snipe(self, ctx: Context):

        if not self.bot.snipes.get(ctx.channel.id, deque()):
            return await ctx.send_error('no recently **deleted** messages')

        msgs = list(self.bot.snipes[ctx.channel.id])
        embeds = list()
        num = 0

        for msg, deleted_at in msgs:
            num += 1
            embed = discord.Embed(color=ctx.author.color, description=msg.content)
            embed.set_author(name=msg.author, icon_url=msg.author.display_avatar)
            embed.set_footer(text=f'deleted {arrow.get(deleted_at).humanize()} | {num} / {len(msgs)}')

            if msg.attachments:
                embed.set_image(url=msg.attachments[0].proxy_url)
            
            embeds.append(embed)

        return await ctx.paginate(embeds)


    @commands.command(
        name='editsnipe',
        aliases=['es'],
        description='snipe a recently edited message'
    )
    async def editsnipe(self, ctx: Context):

        if not self.bot.editsnipes.get(ctx.channel.id, deque()):
            return await ctx.send_error('no recently **edited** messages')

        msgs = list(self.bot.editsnipes[ctx.channel.id])
        embeds = list()
        num = 0

        for before, after in msgs:
            try:
                num += 1
                embed = discord.Embed(color=ctx.author.color, description=before.content)
                embed.set_author(name=before.author, icon_url=before.author.display_avatar)
                embed.set_footer(text=f'edited {arrow.get(after.edited_at).humanize()} | {num} / {len(msgs)}')

                if before.attachments:
                    embed.set_image(url=before.attachments[0].proxy_url)

                embeds.append(embed)
            except:
                continue

        return await ctx.paginate(embeds)


    @commands.command(
        name='reactionsnipe',
        aliases=['rs'],
        description='snipe a recently deleted reaction'
    )
    async def reactionsnipe(self, ctx: Context):

        if not self.bot.reactionsnipes.get(ctx.channel.id, deque()):
            return await ctx.send_error('no recently **deleted** reactions')

        reactions = list(self.bot.reactionsnipes[ctx.channel.id])
        embeds = list()
        num = 0

        for reaction, user, deleted_at in reactions:
            try:
                num += 1
                embed = discord.Embed(color=ctx.author.color, description=f'[{reaction.emoji.name if not isinstance(reaction.emoji, str) else reaction.emoji}]({reaction.message.jump_url})')
                embed.set_author(name=user, icon_url=user.display_avatar)
                embed.set_footer(text=f'deleted {arrow.get(deleted_at).humanize()} | {num} / {len(reactions)}')
                
                embed.set_image(
                    url=(
                        reaction.emoji.url if not isinstance(reaction.emoji, str) 
                        else f"https://em-content.zobj.net/thumbs/240/twitter/322/{'-'.join(unicodedata.name(reaction.emoji).lower().split())}_{ord(reaction.emoji):x}.png"
                    )
                )
                
                embeds.append(embed)
            except:
                continue

        return await ctx.paginate(embeds)


    @commands.command(
        name='removesnipe',
        description='remove the most recent snipe',
        extras={'permissions': 'manage messages'}
    )
    @commands.has_permissions(manage_messages=True)
    async def removesnipe(self, ctx: Context):

        if ctx.channel.id not in self.bot.snipes:
            return await ctx.send_error('there are no recent snipes to remove')

        self.bot.snipes[ctx.channel.id].popleft()
        return await ctx.send_success('successfully **removed** the most recent snipe')


    @commands.command(
        name='removeeditsnipe',
        description='remove the most recent edit snipe',
        extras={'permissions': 'manage messages'}
    )
    @commands.has_permissions(manage_messages=True)
    async def removeeditsnipe(self, ctx: Context):

        if ctx.channel.id not in self.bot.editsnipes:
            return await ctx.send_error('there are no recent edit snipes to remove')

        self.bot.editsnipes[ctx.channel.id].popleft()
        return await ctx.send_success('successfully **removed** the most recent edit snipe')


    @commands.command(
        name='rank',
        description='give yourself a ranked role',
        brief='rank <role>',
        help='rank Developer'
    )
    @commands.bot_has_permissions(manage_roles=True)
    async def rank(self, ctx: Context, role: Union[discord.Role, str]):

        if isinstance(role, str):
            role = ctx.find_role(role)

            if role is None:
                return await ctx.send_error('please provide a **valid** role')

        if role.id not in set(await self.bot.db.fetch('SELECT role_id FROM ranks WHERE guild_id = %s', ctx.guild.id)):
            return await ctx.send_error("that role **isn't a rank** in this server")

        if ctx.author.get_role(role.id) is None:
            if role.position > ctx.guild.me.top_role.position:
                return await ctx.send_error("i can't give that role")

            await ctx.author.add_roles(role, reason=f'rank: used by {ctx.author}')
            return await ctx.send_success(f'you **joined** {role.name}')

        if role.position > ctx.guild.me.top_role.position:
            return await ctx.send_error("i can't remove that role")

        await ctx.author.remove_roles(role, reason=f'rank: used by {ctx.author}')
        return await ctx.send_success(f'you **left** {role.name}')


    @commands.group(
        name='tag',
        aliases=['t'],
        description='see the provided tag',
        brief='tag <tag>',
        help='tag embed',
        invoke_without_command=True
    )
    async def tag(self, ctx: Context, name: Optional[str]):
        
        if name is None:
            return await ctx.send_help()
        
        if not await self.bot.db.fetchrow('SELECT * FROM tags WHERE guild_id = %s AND name = %s', ctx.guild.id, name):
            return await ctx.send_error('there is no existing **tag** with that name')
            
        tag = await self.bot.db.fetchval('SELECT response FROM tags WHERE guild_id = %s AND name = %s', ctx.guild.id, name)
        return await ctx.message.refer().reply(**await utils.to_object(await utils.embed_replacement(ctx.author, tag)))
        

    @tag.command(
        name='add',
        aliases=['create'],
        description='create a new tag for the server',
        brief='tag add <name> <response>',
        help='tag add embed https://vilebot.xyz/embed'
    )
    async def tag_add(self, ctx: Context, name: str, *, response: str):
            
        if await self.bot.db.fetchrow('SELECT * FROM tags WHERE guild_id = %s AND name = %s', ctx.guild.id, name):
            return await ctx.send_error('there is already an existing **tag** with that name')

        await self.bot.db.execute('INSERT INTO tags (guild_id, creator_id, name, response) VALUES (%s, %s, %s, %s)', ctx.guild.id, ctx.author.id, name, response)
        return await ctx.send_success(f"successfully **binded** {name}'s response to:\n\n```{discord.utils.escape_markdown(response)}```")
    

    @tag.command(
        name='remove',
        aliases=['delete'],
        description='remove a tag from the guild',
        brief='tag remove <name>',
        help='tag remove embed'
    )
    async def tag_remove(self, ctx, name: str=None):
            
        if not await self.bot.db.fetchrow('SELECT * FROM tags WHERE guild_id = %s AND name = %s', ctx.guild.id, name):
            return await ctx.send_error('there is no existing **tag** with that name')
  
        await self.bot.db.execute('DELETE FROM tags WHERE guild_id = %s AND name = %s', ctx.guild.id, name)
        return await ctx.send_success(f'successfully **removed** the tag **`{name}`**')
        

    @tag.command(
        name='claim',
        description='claim a tag if the owner left the server',
        aliases=['c'],
        brief='tag claim <name>',
        help='tag claim embed'
    )
    async def tag_claim(self, ctx: Context, name: str):
            
        if not await self.bot.db.fetchrow('SELECT * FROM tags WHERE guild_id = %s AND name = %s', ctx.guild.id, name):
            return await ctx.send_error('there is no existing **tag** with that name')
            
        if ctx.guild.get_member(await self.bot.db.fetchval('SELECT creator_id FROM tags WHERE guild_id = %s AND name = %s', ctx.guild.id, name)) is not None:
            return await ctx.send_error('you cant **claim** that tag')
            
        await self.bot.db.execute('UPDATE tags SET creator_id = %s WHERE guild_id = %s AND name = %s', ctx.author.id, ctx.guild.id, name)
        return await ctx.send_success(f'successfully **claimed** the tag **`{name}`**')
        

    @tag.command(
        name='owner',
        description='get the owner of a tag',
        aliases=['maker', 'own'],
        brief='tag owner <name>',
        help='tag owner embed'
    )
    async def tag_owner(self, ctx: Context, name: str):

        if not await self.bot.db.fetchrow('SELECT * FROM tags WHERE guild_id = %s AND name = %s', ctx.guild.id, name):
            return await ctx.send_success('there is no existing **tag** with that name')
            
        if ctx.guild.get_member(await self.bot.db.fetchval('SELECT creator_id FROM tags WHERE guild_id = %s AND name = %s', ctx.guild.id, name)) is None:
            return await ctx.send_success('the **owner** of this tag has left the guild')
        
        owner = ctx.guild.get_member(await self.bot.db.fetchval('SELECT creator_id FROM tags WHERE guild_id = %s AND name = %s', ctx.guild.id, name))
        return await ctx.send_success(f'{owner.mention}: **{owner}** ( `{owner.id}` )')
        

    @tag.command(
        name='list',
        aliases=['show'],
        description="show a list of the server's tags",
        brief='tag list',
        help='tag list'
    )
    async def tag_list(self, ctx: Context):
        
        if not await self.bot.db.fetchrow('SELECT * FROM tags WHERE guild_id = %s', ctx.guild.id):
            return await ctx.send_error("there aren't any **tags** in this server")
        
        embed = discord.Embed(color=self.bot.color, title=f'Tags in {ctx.guild.name}', description=list())
        for creator_id, name, response in await self.bot.db.execute('SELECT creator_id, name, response FROM tags WHERE guild_id = %s', ctx.guild.id):
            creator = ctx.guild.get_member(creator_id) or 'none'
            embed.description.append(f'{name}\n{self.bot.reply} **creator:** {creator}\n{self.bot.reply} **response:** {response}')
            
        return await ctx.paginate(embed)


    @commands.command(
        name='opticalcharacterrecognition',
        aliases=['ocr'],
        description='extract text from an image',
        brief='ocr <url or attachment>',
        help='ocr ...'
    )
    async def opticalcharacterrecognition(self, ctx: Context, image: Optional[str] = None):

        await ctx.typing()
        if image is None:
            if ctx.message.attachments:
                image = ctx.message.attachments[0].url
            
            else:
                return await ctx.send_help()

        try:
            text = pytesseract.image_to_string(Image.open(io.BytesIO(await self.bot.session.read(image))))
        except:
            return await ctx.send_error('could not extract text from that image')
            
        return await ctx.reply(text)


    @commands.group(
        name='webhook',
        aliases=['wh', 'whook'],
        description='use webhooks through vile',
        brief='webhook <sub command>',
        help='webhook send 1062352112438227027 {content: hi}',
        extras={'permissions': 'manage webhooks'},
        invoke_without_command=True
    )
    @commands.has_permissions(manage_webhooks=True)
    async def webhook(self, ctx: Context):
        return await ctx.send_help()

    
    @webhook.command(
        name='create',
        aliases=['add'],
        description='create a webhook',
        brief='webhook create <name>',
        help='webhook create Friendly Webhook',
        extras={'permissions': 'manage webhooks'}
    )
    @commands.bot_has_permissions(manage_webhooks=True)
    @commands.has_permissions(manage_webhooks=True)
    async def webhook_create(self, ctx: Context, *, name: str):

        await ctx.typing()
        return await ctx.send_success(f'successfully **created** that webhook, use it with this ID: {(await ctx.channel.create_webhook(name=name)).id}')


    @webhook.command(
        name='delete',
        aliases=['remove'],
        description='delete a webhook',
        brief='webhook delete <webhook id>',
        help='webhook delete 1062352112438227027',
        extras={'permissions': 'manage webhooks'}
    )
    @commands.bot_has_permissions(manage_webhooks=True)
    @commands.has_permissions(manage_webhooks=True)
    async def webhook_delete(self, ctx: Context, id: int):
        
        try:
            webhook = await self.bot.fetch_webhook(id)
        except:
            return await ctx.send_error('please provide a **valid** webhook')

        if webhook.guild != ctx.guild:
            return await ctx.send_error('please provide a **valid** webhook in this channel')

        await ctx.typing()
        await webhook.delete()
        return await ctx.send_success(f'successfully **deleted** that webhook')


    @webhook.command(
        name='send',
        aliases=['post'],
        description='send a message through a webhook',
        brief='webhook send <webhook id> <code> [--username]',
        help='webhook send 1062352112438227027 {content: hi}',
        extras={'permissions': 'manage webhooks'}
    )
    @commands.bot_has_permissions(manage_webhooks=True)
    @commands.has_permissions(manage_webhooks=True)
    async def webhook_send(self, ctx: Context, id: int, *, code: str):
        
        try:
            webhook = await self.bot.fetch_webhook(id)
        except:
            return await ctx.send_error('please provide a **valid** webhook')

        if webhook.guild != ctx.guild:
            return await ctx.send_error('please provide a **valid** webhook in this channel')

        await ctx.typing()
        code = code.split(' --username ')
        send = await utils.to_object(await utils.embed_replacement(ctx.author, code[0]))
        send.pop('delete_after')
        send['wait'] = True
        if len(code) > 1:
            send['username'] = code[1]
        msg = await webhook.send(**send)
        return await ctx.send_success(f'successfully **sent** a [message]({msg.jump_url}) using webhook')


    @commands.group(
        name='highlight',
        aliases=['hl'],
        description='make highlights for the server',
        brief='highlight <sub command>',
        help='highlight add glory',
        invoke_without_command=True
    )
    async def highlight(self, ctx: Context):
        return await ctx.send_help()
        

    @highlight.command(
        name='add',
        aliases=['create'],
        description='create a new highlight for the server',
        brief='highlight add <name>',
        help='highlight add glory'
    )
    async def highlight_add(self, ctx: Context, name: str):
            
        if await self.bot.db.fetchrow('SELECT * FROM highlights WHERE guild_id = %s AND name = %s', ctx.guild.id, name):
            return await ctx.send_error('there is already an existing **highlight** with that name')

        await self.bot.db.execute('INSERT INTO highlights (guild_id, creator_id, name) VALUES (%s, %s, %s)', ctx.guild.id, ctx.author.id, name)
        if ctx.guild.id not in self.bot.cache.highlights:
            self.bot.cache.highlights[ctx.guild.id] = dict()

        self.bot.cache.highlights[ctx.guild.id][name] = ctx.author.id
        return await ctx.send_success(f'successfully **added** {name} as a highlight')
    

    @highlight.command(
        name='remove',
        aliases=['delete'],
        description='remove a highlight from the guild',
        brief='highlight remove <name>',
        help='highlight remove glory'
    )
    async def highlight_remove(self, ctx, name: str):
            
        if not await self.bot.db.fetchrow('SELECT * FROM highlights WHERE guild_id = %s AND name = %s', ctx.guild.id, name):
            return await ctx.send_error('there is no existing **highlight** with that name')
  
        await self.bot.db.execute('DELETE FROM highlights WHERE guild_id = %s AND name = %s', ctx.guild.id, name)
        self.bot.cache.highlights[ctx.guild.id].pop(name)

        return await ctx.send_success(f'successfully **removed** the highlight **`{name}`**')


    @highlight.command(
        name='owner',
        description='get the owner of a highlight',
        aliases=['maker', 'own'],
        brief='highlight owner <name>',
        help='highlight owner glory'
    )
    async def highlight_owner(self, ctx: Context, name: str):

        if not await self.bot.db.fetchrow('SELECT * FROM highlights WHERE guild_id = %s AND name = %s', ctx.guild.id, name):
            return await ctx.send_success('there is no existing **highlight** with that name')
            
        if ctx.guild.get_member(await self.bot.db.fetchval('SELECT creator_id FROM highlights WHERE guild_id = %s AND name = %s', ctx.guild.id, name)) is None:
            return await ctx.send_success('the **owner** of this highlight has left the server')
        
        owner = ctx.guild.get_member(await self.bot.db.fetchval('SELECT creator_id FROM highlights WHERE guild_id = %s AND name = %s', ctx.guild.id, name))
        return await ctx.send_success(f'{owner.mention}: **{owner}** ( `{owner.id}` )')
        

    @highlight.command(
        name='list',
        aliases=['show'],
        description="show a list of the server's highlights",
        brief='highlight list',
        help='highlight list'
    )
    async def highlight_list(self, ctx: Context):
        
        if not await self.bot.db.fetchrow('SELECT * FROM highlights WHERE guild_id = %s', ctx.guild.id):
            return await ctx.send_error("there aren't any **highlights** in this server")
        
        embed = discord.Embed(
            color=self.bot.color,
            title=f'Highlights in {ctx.guild.name}',
            description=list()
        )
        for creator_id, name in await self.bot.db.execute('SELECT creator_id, name FROM highlights WHERE guild_id = %s', ctx.guild.id):
            creator = ctx.guild.get_member(creator_id) or 'none'
            embed.description.append(f'{name}\n{self.bot.reply} **creator:** {creator}')
            
        return await ctx.paginate(embed)


    @commands.command(
        name='lookup',
        aliases=['tags'],
        description='search for previously changed usernames',
        brief='lookup <discriminator>',
        help='lookup 0001'
    )
    async def lookup(self, ctx: Context, discriminator: str = '0001'):

        async with ctx.handle_response():
            try:
                int(discriminator)
            except:
                return await ctx.send_error('please provide a **valid** discriminator')

            if int(discriminator) not in range(1, 9999):
                return await ctx.send_error('please provide a **valid** discriminator')

            embed = discord.Embed(
                color=self.bot.color,
                title=f'Recently available {discriminator} tags',
                description=list()
            )

            tags = [(tag, timestamp) for tag, timestamp in await self.bot.db.execute(f'SELECT name, timestamp FROM names WHERE {time.time()} - timestamp < 21600 ORDER BY timestamp DESC') if tag.endswith(f'#{discriminator}')]
            if not tags:
                return await ctx.send_error(f'no recently available tags ending in **{discriminator}** found')
                
            for tag, timestamp in tags:
                if any(list(map(lambda c: c.isalpha() is False, tag[:-5].replace(' ', '')))) is False:
                    embed.description.append(f"{tag}   \u2022   {discord.utils.format_dt(datetime.fromtimestamp(timestamp), style='R')}")

            if not embed.description:
                return await ctx.send_error(f'no recently available tags ending in **{discriminator}** found')
                
            return await ctx.paginate(embed)


    @commands.hybrid_command(
        name='wolfram',
        aliases=['w'],
        description='search for information using wolfram',
        brief='wolfram <query>',
        help='wolfram what is 5 minutes in seconds'
    )
    async def wolfram(self, ctx: Context, *, query: str):
        
        if ctx.interaction:
            await ctx.interaction.response.defer(thinking=True)
            
        async with ctx.handle_response():
            api = 'http://api.wolframalpha.com/v1/result'
            params = {
                'appid': '46HPQ5-725AAXQ5TY', 
                'i': query, 
                'output': 'json', 
                'units': 'metric'
            }
        
            data = await self.bot.session.text(api, params=params)
        
            if data == 'Wolfram|Alpha did not understand your input':
                return await ctx.send_error("sorry, i couldn't understand your question")
            
            return await ctx.reply(data.replace('Wolfram Alpha', 'Vile'))


    @commands.command(
        name='afk',
        aliases=['away'],
        description='go afk and warn people who mention you',
        brief='afk <status>',
        help='afk sleeping :zzz:'
    )
    async def afk(self, ctx: Context, *, status: str = 'AFK'):

        if len(status) > 255:
            return await ctx.send_error('please provide a **valid** status under 255 characters')

        await self.bot.db.execute('INSERT INTO afk (user_id, guild_id, status, lastseen) VALUES (%s, %s, %s, %s)', ctx.author.id, ctx.guild.id, status, int(time.time()))
        if ctx.author.id not in self.bot.cache.afk:
            self.bot.cache.afk[ctx.author.id] = list()

        self.bot.cache.afk[ctx.author.id].append({'guild_id': ctx.guild.id, 'status': status, 'lastseen': int(time.time())})
        return await ctx.send_success(f"you're now afk with the status **{status}**")


    @commands.command(
        name='translate',
        aliases=['tr'],
        description='translate text to a language of your choice',
        brief='translate <language> <text>',
        help='translate english hola soy dora'
    )
    async def translate(self, ctx: Context, language: str, *, text: str):
        
        async with ctx.handle_response():
            trans = GoogleTranslator(source='auto', target=language)

            try:
                return await ctx.reply(await asyncio.to_thread(lambda: trans.translate(text=text)))
            except:
                return await ctx.send_error('failed to **translate** the provided text')


    @commands.group(
        name='birthday',
        aliases=['bday', 'bd'],
        description='set your birthday',
        brief='birthday set <birthday>',
        help='birthday set May 15',
        invoke_without_command=True
    )
    async def birthday(self, ctx: Context, user: typing.Optional[Union[discord.Member, discord.User]] = commands.Author):
        
        bday = await self.bot.db.fetchval('SELECT birthday FROM birthdays WHERE user_id = %s', user.id)
        if not bday:
            return await ctx.send_error(f"{user.name} doesn't have their birthday set")
            
        return await ctx.send_success(f"{user.name}'s birthday is on **{bday}**")
        

    @birthday.command(
        name='set',
        description='set your birthday',
        brief='birthday set <birthday>',
        help='birthday set May 15'
    )
    async def birthday_set(self, ctx: Context, *, bday: str):
        
        bdays = bday.split()
        if len(bdays) <= 1 or len(bdays) > 2:
            return await ctx.send_error('please provide a **valid** birthday')
            
        if bdays[0] not in [
            'January', 'February',
            'March', 'April',
            'May', 'June',
            'July', 'August',
            'September', 'October',
            'November', 'December'] or int(bdays[1]) not in range(1, 31):
            return await ctx.send_error('please provide a **valid** birthday')
            
        await self.bot.db.execute('INSERT INTO birthdays (user_id, birthday) VALUES (%s, %s) ON DUPLICATE KEY UPDATE birthday = VALUES(birthday)', ctx.author.id, bday)
        return await ctx.send_success(f'successfully **binded** your birthday to **`{bdays[0]} {bdays[1]}`**')

    @commands.command(
        name='marry',
        description='marry a user through the bot',
        brief='marry <user>',
        help='marry @glory#0007'
    )
    async def marry(self, ctx: Context, user: discord.Member):

        if user == ctx.author:
            return await ctx.send_error("you can't **marry** yourself")

        if user == ctx.guild.me:
            return await ctx.send_error("you can't **marry** me")

        if user.bot:
            return await ctx.send_error("you can't **marry** a bot")

        if await self.bot.db.fetchval('SELECT partner FROM marriage WHERE user_id = %s', ctx.author.id):
            return await ctx.send_error("you're already **married**")

        from utilities.confirmation import confirm

        message = await ctx.send_error(f'{ctx.author.name} wants to **marry** you, do you accept?')
        alt_ctx = copy.copy(ctx)
        alt_ctx.author = user
        conf = await confirm(ctx=alt_ctx, message=message)
        if conf is True:
            await self.bot.db.execute('INSERT INTO marriage (user_id, partner, since) VALUES (%s, %s, %s)', ctx.author.id, user.id, int(datetime.now().timestamp()))
            await self.bot.db.execute('INSERT INTO marriage (user_id, partner, since) VALUES (%s, %s, %s)', user.id, ctx.author.id, int(datetime.now().timestamp()))
            return await message.edit(
                embed=discord.Embed(
                    color=self.bot.color,
                    description=f"{self.bot.done} {ctx.author.mention}**:** :heart: you're now **married** to **{user}**"
                )
            )

        return await ctx.send_error(f'sorry, {user.mention} **rejected** your proposal :frowning:')

    @commands.command(
        name='marriage',
        aliases=['partner'],
        description='see who you are married to'
    )
    async def marriage(self, ctx: Context, user: Union[discord.Member, discord.User] = commands.Author):

        partner = self.bot.get_user(await self.bot.db.fetchval('SELECT partner FROM marriage WHERE user_id = %s', user.id))
        if partner is None:
            return await ctx.send_error(f"{user.name} doesn't have a **partner**")
        
        since=await self.bot.db.fetchval('SELECT since FROM marriage WHERE user_id = %s', user.id)
        return await ctx.send_success(f'{"you are" if user == ctx.author else f"{user.name} is"} currently **married** to **{partner}**\n{self.reply} {"you have" if user == ctx.author else f"{user.name} has"} been **married** for **{arrow.get(since).humanize(only_distance=True)}**')

    @commands.command(
        name='divorce',
        description='divorce your current partner'
    )
    async def divorce(self, ctx: Context):

        partner = self.bot.get_user(await self.bot.db.fetchval('SELECT partner FROM marriage WHERE user_id = %s', ctx.author.id))
        if partner is None:
            return await ctx.send_error("you don't have a **partner**")

        from utilities.confirmation import confirm
        
        message = await ctx.send_error(f'are you **sure** you want to divorce **{partner}**')
        conf = await confirm(ctx=ctx, message=message)
        if conf is True:
            await self.bot.db.execute('DELETE FROM marriage WHERE user_id = %s', ctx.author.id)
            await self.bot.db.execute('DELETE FROM marriage WHERE user_id = %s', partner.id)
            return await message.edit(embed=discord.Embed(
                color=self.bot.color,
                description=f'{self.bot.done} {ctx.author.mention}**:** you **divorced {partner}**'
            ))

        return await message.delete()


    @commands.command(
        name='quote',
        description='quote the provided message',
        brief='quote <message>',
        help='quote 1060070470239662081'
    )
    async def quote(self, ctx: Context, message: Optional[discord.Message] = None):

        if not message:
            if not ctx.message.reference:
                return await ctx.send_help()

            message = ctx.message.reference.resolved
        

        embed = discord.Embed(color=0x2f3136)
        empty = '\u200b'
        embed.description = f'{empty if not message.content else message.content}'
        embed.set_author(name=message.author, icon_url=message.author.display_avatar)
        if message.attachments:
            embed.set_image(url=message.attachments[0].proxy_url)
        
        embeds = []
        embeds.append(embed)
        for e in message.embeds:
            embeds.append(e)

        return await ctx.reply(embeds=embeds, view=discord.ui.View().from_message(message))


    @commands.hybrid_command(
        name='texttospeech',
        aliases=['tts'],
        description='convert text to a mp3 file',
        brief='texttospeech <language> <text>',
        help='texttospeech en hello, my name is glory'
    )
    async def texttospeech(self, ctx: Context, language: str, *, text: str):
        if ctx.interaction:
            await ctx.interaction.response.defer(thinking=True)

        return await ctx.reply(file=discord.File(await utils.text_to_speech(language, text), f'{text}.mp3'))


    @commands.command(
        name='pp',
        aliases=['ppsize', 'dick', 'penis'],
        description='view your dick size',
        brief=',pp <user>',
        help=',pp @glory#0007'
    )
    async def pp(self, ctx: Context, member: discord.Member = commands.Author):

        pp_size = random.randint(1, 20)
        if pp_size in [1, 2]:
            return await ctx.reply("i couldn't find this nigga's penis, try looking somewhere else")

        if member.id == 1051945999570051102:
            return await ctx.reply("i couldn't find this nigga's penis, try looking somewhere else")

        return await ctx.reply(
            embed=discord.Embed(
                color=self.bot.color,
                title=f"{member.name}'s penis",
                description=f"8{''.join(['=' for i in range(pp_size)])}D"
            )
        )


    @commands.command(
        name='pack',
        description='pack the mentioned member',
        brief='pack <member>',
        help='pack @glory#0007'
    )
    @commands.cooldown(1, 5, commands.BucketType.default)
    async def pack(self, ctx: Context, member: discord.Member):
        return await utils.pack(ctx, member)


    @commands.hybrid_command(
        name='posts',
        aliases=['weheartitposts', 'whiposts'],
        description="show a user's weheartit posts",
        brief='posts <user>',
        help='posts glory'
    )
    async def posts(self, ctx: Context, user: str):
        
        if ctx.interaction:
            await ctx.interaction.response.defer(thinking=True)

        async with ctx.handle_response():
            embeds = list()
            async for post in utils.getwhiuser(user):
                embeds.append(discord.Embed(color=await utils.dominant_color(post)).set_image(url=post))

            return await ctx.paginate(embeds)


    @commands.hybrid_command(
        name='screenshot',
        aliases=['ss'],
        description='screenshot a website using the bot',
        brief='screenshot <url>',
        help='screenshot https://vilebot.xyz'
    )
    async def screenshot(self, ctx: Context, url: str):

        if ctx.interaction:
            await ctx.interaction.response.defer(thinking=True)
            
        async with ctx.handle_response():
            async with aiohttp.ClientSession() as session:
                async with session.get('https://api.microlink.io', params={'url': url, 'screenshot': 'True'}, proxy=None) as resp:
                    data = await resp.json()
            
            if data['status'] == 'fail':
                return await ctx.send_success('please provide a **valid** website')

            
            return await ctx.reply(file=await utils.file(data['data']['screenshot']['url']))


    @commands.command(
        name='transparent',
        description='make the background of an image transparent',
        brief='transparent <url or attachment>',
        help='transparent ...'
    )
    async def transparent(self, ctx: Context, image: Optional[str] = None):

        if image is None:
            if not ctx.message.attachments:
                return await ctx.send_error('please provide a **valid** image')

            image = ctx.message.attachments[0].url

        async with ctx.handle_response():
            return await ctx.reply(file=discord.File(await utils.remove_background(image), f'vile transparent.png'))


    @commands.command(
        name='wordcloud',
        aliases=['wc'],
        description="generate an image containing this channel's message",
        brief='wordcloud [limit]',
        help='wordcloud 500'
    )
    async def wordcloud(self, ctx: Context, limit: int = 507):

        to_delete = await ctx.send_success(f'generating **word cloud** with the past **{100 if limit == 507 else utils.intword(limit)}** messages')

        async with ctx.handle_response():
            
            wc = await utils.create_wordcloud([m.content async for m in ctx.channel.history(limit=limit)], limit=limit)
            await to_delete.delete()
            return await ctx.reply(
                content=f'Successfully generated a **word cloud** with the past **{100 if limit == 507 else utils.intword(limit)}** messages', file=discord.File(wc, 'vile wordcloud.png')
            )
        
    
    @commands.command(
        name='uwuify',
        aliases=['uwu'],
        description='uwuify the given text',
        brief='uwuify <text>',
        help='uwuify hello! my name is glory.'
    )
    async def _uwuify(self, ctx: Context, *, text: str):
        return await ctx.reply(uwupy.uwuify_str(text))


    @commands.command(
        name='selfpurge',
        aliases=['cs'],
        description='purge messages from yourself'
    )
    @commands.bot_has_permissions(manage_messages=True)
    async def selfpurge(self, ctx: Context):
        return await ctx.send_success(
            f"successfully **purged** {len(await ctx.channel.purge(limit=101, check=lambda m: m.author == ctx.author))} messages from {ctx.author.mention}"
        )



    @commands.command(
        name='8ball',
        aliases=['8b'],
        description='ask the 8ball a question',
        brief='8ball <prompt>',
        help='8ball why did jenna ortega reject me'
    )
    async def eightball(self, ctx, *, prompt: str):
            
        responses = [
            "As I see it, yes.",
            "Ask again later.",
            "Better not tell you now.",
            "Cannot predict now.",
            "Concentrate and ask again.",
            "Don’t count on it.",
            "It is certain.",
            "It is decidedly so.",
            "Most likely.",
            "My reply is no.",
            "My sources say no.",
            "Looks not so good.",
            "Looks good.",
            "Reply hazy, try again.",
            "Signs point to yes.",
            "Very doubtfub.",
            "Without a doubt.",
            "Yes.",
            "Yes – definitely.",
            "You may rely on it.",
            "*hmm*"
        ]
        
        return await ctx.reply(f'{prompt}\n> {random.choice(responses)}')


    @commands.group(
        name='soundcloud',
        aliases=['sc'],
        description='interact with soundcloud using vile',
        brief='soundcloud <sub command>',
        help='soundcloud search jaded sadeyes',
        invoke_without_command=True
    )
    async def soundcloud(self, ctx: Context):
        return await ctx.send_help()
        

    @soundcloud.command(
        name='search',
        aliases=['find'],
        description='search for a specific song',
        brief='soundcloud search <song>',
        help='soundcloud search jaded sadeyes'
    )
    async def soundcloud_search(self, ctx: Context, *, query: str):
        
        async with ctx.handle_response():
            data = await utils.get_video_data(f'scsearch:{query}')
        
            if not data['entries']:
                return await ctx.send_error('no results found')
            
            return await utils.get_soundcloud(ctx, self.bot, data['entries'][0]['original_url'])
   

async def setup(bot: commands.Bot):
    await bot.add_cog(Miscellaneous(bot))
