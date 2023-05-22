import discord, json, tempfile, shutil, re, os,datetime,typing
from discord.ext import commands
from modules import Message, DL, DisplayName, util, permissions

class embed(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.color=self.bot.color
        self.url_regex = re.compile(r"(http|ftp|https)://([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?")

    def _get_embed_from_json(self, ctx, embed_json):
        # Helper method to ensure embed_json is valid, and doesn't bypass limits
        # Let's attempt to serialize the json
        try:
            embed_dict = json.loads(embed_json)
            # Let's parse the author and color
            if embed_dict.get("color") and not isinstance(embed_dict["color"],list):
                # We got *something* for the color - let's first check if it's an int between 0 and 16777215
                if not isinstance(embed_dict["color"],int) or not 0<=embed_dict["color"]<=16777215:
                    color_value = None
                    if str(embed_dict["color"]).lower().startswith(("#","0x")):
                        # Should be a hex color code
                        try:
                            color_value = int(str(embed_dict["color"]).lower().lstrip("#").lstrip("0x"),16)
                            if not 0<=color_value<=16777215: color_value = None # Out of range
                        except:
                            pass
                    # Let's try to resolve it to a user
                    embed_dict["color"] = color_value if color_value is not None else "#303135"
            #if embed_dict.get("author") and not isinstance(embed_dict["author"],dict):
                # Again - got *something* for the author - try to resolve it
                #embed_dict["author"] = DisplayName.memberForName(str(embed_dict["author"]),ctx.guild)
            if embed_dict.get("timestamp"):
                #ts=embed_dict.get("timestamp")
                #embed_dict["timestamp"]=datetime.datetime.strptime(ts, format=)
                dt=datetime.datetime.now().timestamp()
                embed_dict["timestamp"]=f"{dt}"
        except Exception as e:
            return e
        # Only allow owner to modify the limits
        if not commands.is_owner():
            embed_dict["title_max"] = 256
            embed_dict["desc_max"] = 2048
            embed_dict["field_max"] = 25
            embed_dict["fname_max"] = 256
            embed_dict["fval_max"] = 1024
            embed_dict["foot_max"] = 2048
            embed_dict["auth_max"] = 256
            embed_dict["total_max"] = 6000
        return embed_dict

    async def embed_replacement(self,user,guild,params):
        if "{user}" in params:
            params = params.replace("{user}", str(user))
        if "{user.mention}" in params:
            params = params.replace("{user.mention}", str(user.mention))
        if "{user.name}" in params:
            params = params.replace("{user.name}", str(user.name))
        if "{user.avatar}" in params:
            params = params.replace("{user.avatar}", str(user.display_avatar.url))
        if "{user.joined_at}" in params:
            params = params.replace("{user.joined_at}", discord.utils.format_dt(user.joined_at, style="R"))
        if "{user.created_at}" in params:
            params=params.replace("{user.created_at}", discord.utils.format_dt(user.created_at, style="R"))
        if "{user.discriminator}" in params:
            params = params.replace("{user.discriminator}", str(user.discriminator))
        if "{guild.name}" in params:
            params = params.replace("{guild.name}", str(user.guild.name))
        if "{guild.count}" in params:
            params = params.replace("{guild.count}", str(user.guild.member_count))
        if "{guild.id}" in params:
            params = params.replace("{guild.id}", str(user.guild.id))
        if "{guild.created_at}" in params:
            params = params.replace("{guild.created_at}", discord.utils.format_dt(user.guild.created_at, style="R"))
        if "{guild.boost_count}" in params:
            params = params.replace("{guild.boost_count}", str(user.guild.premium_subscription_count))
        if "{guild.boost_tier}" in params:
            params = params.replace("{guild.boost_tier}", str(user.guild.premium_tier))
        if "{guild.icon}" in params:
            params = params.replace("{guild.icon}", str(user.guild.icon.url))
        return params

    @commands.command(name='format')
    @commands.has_permissions(administrator=True)
    async def format(self, ctx, *, params):
        user = ctx.author
        guild= ctx.guild
        if params:
            params=params.replace("{embed}","")
            params=await util.embed_replacement(user,guild,params)
            em = await self.to_embed(ctx,user,ctx.guild,params)
            # try:
            #     await ctx.send(embed=em)
            #     self._last_embed = params
            # except Exception as e:
            #     await ctx.send(e)
        else:
            await ctx.send(params)

    @commands.command(name='newembedsteal')
    async def newembedsteal(self, ctx, message_url):
        if message_url is None: return await ctx.reply(embed=discord.Embed(color=self.color, description=f"{self.bot.no} {ctx.author.mention}: **provide a message url**"))
        parts = [x for x in message_url.replace("/"," ").split() if len(x)]
        try: 
            channel_id,message_id = [int(x) for x in parts[-2:]]
        except: 
            try: 
                channel_id = ctx.channel.id
                message_id = message_url
            except:
                return await ctx.reply(embed=discord.Embed(color=self.color, description=f"{self.bot.no} {ctx.author.mention}: **invalid message url**"))
        guild = ctx.guild
        if len(parts) > 2:
            if parts[-3].lower() == "@me":
                guild = self.bot
            else:
                try: guild = self.bot.get_guild(int(parts[-3]))
                except: pass
        if guild is None:
            guild = ctx.guild if ctx.guild else self.bot
        channel = guild.get_channel(channel_id)
        if not channel: return await ctx.reply(color=self.color, embed=discord.Embed(description=f"{self.bot.no} {ctx.author.mention}: i couldn't find the channel connected to that id"))
        try: message = await channel.fetch_message(message_id)
        except: return await ctx.reply(embed=discord.Embed(color=self.color, description=f"{self.bot.no} {ctx.author.mention}: i couldn't find the message connected to that id"))
        q=""
        if message.embeds:
            e=message.embeds[0]
            q="{embed}"
            if e.color:
                q+=f"{color: {e.color}}$v"
            if e.description:
                q+=f"{description: {e.description}}$v"
            if e.title:
                q+=f"{title: {e.title}}$v"
            if e.footer:
                r=""
                if e.footer.text:
                    r+=f"footer: {e.footer.text}"
                if e.footer.icon_url: r+=f" && icon: {e.footer.icon_url}"
                q+=f"{{r}}$v"
            if e.fields:
                for f in e.fields:
                    q+=f"{field: {f.name} && value: {f.value} && inline: {f.inline}}$v"
            if e.url:
                q+=f"{url: {e.url}}$v"
            if e.timestamp:
                q+=f"{timestamp: true}$v"
            if e.author:
                r=""
                if e.author.name:
                    r+=f"author: {e.author.name}"
                if e.author.icon_url:
                    r+=f" && icon: {e.author.icon_url}"
                if e.author.url:
                    r+=f" && url: {e.author.url}"
                q+=f"{{r}}$v"
            if e.image:
                q+=f"{image: {e.image.url}}$v"
            if e.thumbnail:
                q+=f"{thumbnail: {e.thumbnail.url}}$v"
        if message.components:
            for cp in message.components:
                for child in cp.children:
                    if child.url and child.label:
                        if child.emoji:
                            ddddddddd=f'&& {child.emoji} '
                        else:
                            ddddddddd=""
                        if child.label:
                            dddddddddd=f"label: {child.label} && "
                        qqqqqqqqqq+=f"{dddddddddd}link: {child.url}{ddddddddd}"
                        q+=f"{{qqqqqqqqqq}}$v"
        if len(q) > 1:
            return await util.send_good(ctx, f"successfully copied embed\n```{q}```")



    async def to_embed(self,ctx,user,guild,params):
        em = discord.Embed()
        if "label:" in params or "emoji:" in params:
            view = discord.ui.View()
        else:
            view=None
        if not params.count('{'):
            if not params.count('}'):
                em.description = params
        #if "title" in params or "description" in params:
        if "description:" in params or "title:" in params or "image:" in params or "thumbnail:" in params or "field:" in params:
            for field in util.get_parts(params):
                data = util.parse_field(field)
                content = data.get('content') or None
                color = data.get('color') or data.get('colour')
                if color == 'random':
                    em.color = random.randint(0, self.color)
                elif color == 'chosen':
                    maybe_col = os.environ.get('COLOR')
                    if maybe_col:
                        raw = int(maybe_col.strip('#'), 16)
                        return discord.Color(value=raw)
                    else:
                        return await ctx.send('color error')
                elif color:
                    color = int(color.strip('#'), 16)
                    em.color = discord.Color(color)
                if data.get('description'):
                    em.description = data['description']
                if data.get('desc'):
                    em.description = data['desc']
                if data.get('title'):
                    em.title = data['title']
                if data.get('url'):
                    em.url = data['url']
                author = data.get('author')
                icon, url = data.get('icon'), data.get('url')

                if author:
                    em._author = {'name': author}
                    if icon:
                        em._author['icon_url'] = icon
                    if url:
                        em._author['url'] = url

                label,link = data.get("label") or None, data.get("link" or None)
                label,link,emoji = data.get("label") or None, data.get("link" or None),data.get('emoji' or None)
                if label:
                    if link:
                        url=link
                        view.add_item(discord.ui.Button(label=label, emoji=emoji, url=url))
                else:
                    if link:
                        if emoji:
                            view.add_item(discord.ui.Button(label=label, emoji=emoji, url=link))

                field, value = data.get('field'), data.get('value')
                inline = False if str(data.get('inline')).lower() == 'false' else True
                if field and value:
                    em.add_field(name=field, value=value, inline=inline)

                if data.get('thumbnail'):
                    em._thumbnail = {'url': data['thumbnail']}

                if data.get('image'):
                    em._image = {'url': data['image']}

                if data.get('delete'):
                    delete=int(data['delete'])
                else:
                    delete=None

                if data.get('footer'):
                    em._footer = {'text': data.get('footer')}
                    if data.get('icon'):
                        em._footer['icon_url'] = data.get('icon')

                if 'timestamp' in data.keys() and len(data.keys()) == 1:
                    em.timestamp = datetime.datetime.now()
        else:
            em=None
            for field in util.get_parts(params):
                data = util.parse_field(field)
                if data.get('delete'):
                    delete=int(str(data['delete']))
                else:
                    delete=None
                if data.get('content'):
                    content=data['content']
                else:
                    content=None
                label,link,emoji = data.get("label") or None, data.get("link" or None),data.get('emoji' or None)
                if label:
                    if link:
                        url=link
                        view.add_item(discord.ui.Button(label=label, emoji=emoji, url=url))
                else:
                    if link:
                        if emoji:
                            view.add_item(discord.ui.Button(label=label, emoji=emoji, url=link))

        message=await ctx.send(delete_after=delete,content=content, embed=em, view=view)
        return message


    def get_parts(self, string):
        '''
        Splits the sections of the embed command
        '''
        for i, char in enumerate(string):
            if char == "(":
                ret = ""
                while char != ")":
                    i += 1
                    char = string[i]
                    ret += char
                yield ret.rstrip(')')

    def parse_field(self, string):
        '''
        Recursive function to get all the key val
        pairs in each section of the parsed embed command
        '''
        ret = {}

        parts = string.split(':')
        key = parts[0].strip().lower()
        val = ':'.join(parts[1:]).strip()

        ret[key] = val

        if '&&' in string:
            string = string.split('&&')
            for part in string:
                ret.update(self.parse_field(part))
        return ret

    @commands.command(name='embed', extras={'perms', 'manage messages'}, description='send an embed using a json', brief='type,embedjson', aliases=['ce','createembed'])
    @commands.has_permissions(manage_messages=True)
    async def embed(self, ctx, *, embed_json = None):
        if embed_json.startswith("{json}"):
            type='json'
            embed_json=embed_json.strip("{json}")
        else:
            type="rival"
        """Builds an embed using json formatting.
        Accepts json passed directly to the command, or an attachment/url pointing to a json file.
        ----------------------------------
        Options     (All):
        pm_react        (str)
        title           (str)
        page_count      (bool)
        url             (str)
        description     (str)
        image           (str or dict { url })
        footer          (str or dict { text, icon_url })
        thumbnail       (str or dict { url })
        author          (str, dict { name, url, icon_url }, or user/member)
        color           (user/member, rgb int array, int)
        ----------------------------------
        Options      (field only):
        fields       (list of dicts { name (str), value (str), inline (bool) })
        ----------------------------------
        Options      (text only):
        d_header     (str)
        d_footer     (str)
        max_pages    (int)
        ----------------------------------
        Example: !embed {"title":"An embed!","description":"This is an embed"}
        """
        try:
            if type.lower() == "json":
                view = discord.ui.View()
                view.add_item(discord.ui.Button(style=discord.ButtonStyle.link, label=f'here', url="https://rival.rocks/embed"))
                if embed_json == "help":
                    return await ctx.reply(view=view,embed=discord.Embed(color=self.color,title="Rival Embed Creator", url="https://rival.rocks/embed"))
                if embed_json is None and not len(ctx.message.attachments):
                    return await ctx.send(view=view,embed=discord.Embed(color=self.color,title="Rival Embed Creator", url="https://rival.rocks/embed"))
                user = ctx.author
                guild= ctx.guild
                params=embed_json
                if params.startswith('{embed}'):
                    params = params.replace('{embed}', '')
                    if "{user}" in params:
                        params = params.replace("{user}", str(user))
                    if "{user.mention}" in params:
                        params = params.replace("{user.mention}", str(user.mention))
                    if "{user.name}" in params:
                        params = params.replace("{user.name}", str(user.name))
                    if "{user.avatar}" in params:
                        params = params.replace("{user.avatar}", str(user.avatar.url))
                    if "{user.joined_at}" in params:
                        params = params.replace("{user.joined_at}", discord.utils.format_dt(user.joined_at, style="R"))
                    if "{user.discriminator}" in params:
                        params = params.replace("{user.discriminator}", str(user.discriminator))
                    if "{guild.name}" in params:
                        params = params.replace("{guild.name}", str(ctx.guild.name))
                    if "{guild.count}" in params:
                        params = params.replace("{guild.count}", str(user.guild.member_count))
                    if "{guild.id}" in params:
                        params = params.replace("{guild.id}", str(user.guild.id))
                    if "{guild.created_at}" in params:
                        params = params.replace("{guild.created_at}", discord.utils.format_dt(user.guild.created_at, style="R"))
                    if "{guild.boost_count}" in params:
                        params = params.replace("{guild.boost_count}", str(user.guild.premium_subscription_count))
                    if "{guild.boost_tier}" in params:
                        params = params.replace("{guild.boost_tier}", str(user.guild.premium_tier))
                    if "{guild.icon}" in params:
                        params = params.replace("{guild.icon}", str(user.guild.icon.url))
                    params=await self.embed_replacement(user,guild,params)
                    return await self.to_embed(ctx,user,ctx.guild,params)
                    # try:
                    #     await ctx.send(embed=em)
                    #     self._last_embed = params
                    # except Exception as e:
                    #     await ctx.send(e)
                if embed_json is None: return await ctx.send_help(ctx.command)
                if "\\n" in embed_json:
                    embed_json=embed_json.replace('\\\\','\\')

                no_dm = "-nodm" in embed_json.lower().split()[:2]

                # Check for attachments - and try to load/serialize the first
                if len(ctx.message.attachments):
                    try: embed_json = await DL.async_text(ctx.message.attachments[0].url)
                    except: return await Message.EmbedText(color=self.color, description=f"{self.bot.no} {ctx.author.mention}: "+"could not download that url.").send(ctx)
                else:
                    # Strip out the no_dm if found
                    if no_dm:
                        embed_json = re.sub("(?i)-nodm","",embed_json,count=1).strip()
                    if self.url_regex.match(embed_json):
                        # It's a URL - let's try to download it
                        try: embed_json = await DL.async_text(embed_json)
                        except: return await Message.EmbedText(color=self.color, description=f"{self.bot.no} {ctx.author.mention}: "+"could not download that url.").send(ctx)
                if "$(" in embed_json:
                    try:
                        jd=[]
                        kd=[]
                        jd=embed_json.split("$")
                        for jd in jd:
                            result = jd[jd.find('(')+1:jd.find(')')]
                            kd.append(result)
                        kd.pop(0)
                        for kd in kd:
                            embed_json=embed_json.replace(f"$({kd})", f"{eval(kd)}")
                    except:
                        pass
                embedd=json.loads(embed_json)
                if not embedd.get("description") and not embedd.get("title") and embedd.get("content"):
                    delete=embedd.get("autodelete", None)        
                    return await ctx.send(delete_after=delete, content=embedd["content"])
                embed_dict = self._get_embed_from_json(ctx,embed_json)
                if isinstance(embed_dict,Exception):
                    return await Message.EmbedText(title="Something went wrong...", description=str(embed_dict)).send(ctx)
                if no_dm and permissions.is_owner():
                    embed_dict["pm_after_fields"] = -1
                else:
                    # We don't have perms to set this - remove them if they exist
                    embed_dict.pop("pm_after_fields",None)
                    embed_dict.pop("pm_after_pages",None)
                try:
                    # Hard limit of 10 messages
                    embed_dict["max_pages"] = 10
                    await Message.Embed(**embed_dict).send(ctx)
                except Exception as e:
                    try: e = str(e)
                    except: e = "An error occurred :("
                    await Message.EmbedText(title="Something went wrong...", description=e).send(ctx)
            else:
                user = ctx.author
                guild = ctx.guild
                params=embed_json
                if params:
                    params=params.replace("{embed}","")
                    params=await util.embed_replacement(user,guild,params)
                    em = await self.to_embed(ctx,user,ctx.guild,params)
                    # try:
                    #     await ctx.send(embed=em)
                    #     self._last_embed = params
                    # except Exception as e:
                    #     await ctx.send(e)
                else:
                    await ctx.send(params)
        except Exception as e:
            return await util.send_error(ctx, f"error occured\n```{e}```")

    @commands.command(hidden=True, aliases=['embedsend'], extras={'perms', 'manage messages'})
    @commands.has_permissions(manage_messages=True)
    async def post(self, ctx, channel_id = None, *, embed_json = None):
        """Builds an embed using json formatting and sends it to the specified channel (bot-admin only).
        Accepts json passed directly to the command, or an attachment/url pointing to a json file.

        The json follows the same guidelines as the embed command - with the addition of the following:

        before    (str - an optional message to send before the embed)
        after     (str - an optional message to send after the embed)
        message   (str - alias to after)

        ----------------------------------

        Example: $post 1234567890 {"title":"An embed!","description":"This is an embed","message":"Text after the embed!"}
        """
        if not ctx.guild: return await ctx.send(embed=discord.Embed(color=self.color, description="`{}post` can only be ran in a guild".format(ctx.prefix)))
        if channel_id is None or (embed_json is None and not len(ctx.message.attachments)):
            return await ctx.send(embed=discord.Embed(color=self.color, description=f"{self.bot.no} {ctx.author.mention}: "+"`{}post [channel_id] [embed_json]` - see the `{}help embed` output for formatting details.".format(ctx.prefix,ctx.prefix)))
        channel = DisplayName.channelForName(channel_id,ctx.guild)
        if not channel: return await ctx.send(embed=discord.Embed(color=self.color, description=f"{self.bot.no} {ctx.author.mention}: could not find that channel"))

        # Check for attachments - and try to load/serialize the first
        if len(ctx.message.attachments):
            try: embed_json = await DL.async_text(ctx.message.attachments[0].url)
            except: return await Message.EmbedText(color=self.color, description=f"{self.bot.no} {ctx.author.mention}: "+"could not download that url.").send(ctx)
        else:
            if self.url_regex.match(embed_json):
                # It's a URL - let's try to download it
                try: embed_json = await DL.async_text(embed_json)
                except: return await Message.EmbedText(color=self.color, description=f"{self.bot.no} {ctx.author.mention}: "+"could not download that url.").send(ctx)
        embed_dict = self._get_embed_from_json(ctx,embed_json)
        if isinstance(embed_dict,Exception):
            return await Message.EmbedText(title="Something went wrong...", description=str(embed_dict),color=ctx.author).send(ctx)
        # Make sure we have *something* to post
        required = ["title","description","fields","before","after","message"]
        if not any((x in embed_dict for x in required)):
            return await Message.EmbedText(
                color=self.color, description=f"{self.bot.no} {ctx.author.mention}: "+"The passed json data is missing one or more required field.\nIt needs at least one of the following:\n```\n{}\n```".format("\n".join(required)),
            ).send(ctx)
        # Don't ever pm as we're posting
        embed_dict["pm_after_fields"] = -1
        return_message = None
        try:
            # Check for a message to send before
            if embed_dict.get("before"):
                return_message = await channel.send(str(embed_dict["before"][:2000]),allowed_mentions=discord.AllowedMentions.all())
            # Make sure we have either fields or description - might just be
            # a message we're sending
            if any((x in embed_dict for x in ("fields","description","title"))):
                # Hard limit of 10 messages
                embed_dict["max_pages"] = 10
                return_message = await Message.Embed(**embed_dict).send(channel)
            # Check for a message to send after
            if embed_dict.get("after",embed_dict.get("message")):
                return_message = await channel.send(str(embed_dict.get("after",embed_dict.get("message"))[:2000]),allowed_mentions=discord.AllowedMentions.all())
        except Exception as e:
            try: e = str(e)
            except: e = "An error occurred :("
            return await Message.EmbedText(title="Something went wrong...", description=e).send(ctx)
        # If we got here - it posted successfully to a different channel,
        # let's send a confirmation message with a link to the successful post.
        if return_message and not ctx.channel == channel:
            await Message.EmbedText(
                title="Post Successful",
                color=ctx.author,
                description="Last message sent [here]({}).".format(return_message.jump_url)
            ).send(ctx)

    @commands.command(name='embedsteal', extras={'perms':'manage messages'}, aliases=['embedcode', 'getembed'], usage="```Swift\nSyntax: !embedsteal <type> <message url>\nExample: !embedsteal rival https://discord.com/channels/905585227269832734/905605967285211146/957383671688601691```",description='get code from an embed', brief='type,message_url')
    @commands.has_permissions(manage_messages=True)
    async def embedsteal(self, ctx, message_url=None, kind="rival"):
        if not kind: kind=='rival'
        if not message_url:
            return await util.send_error(ctx, f"please include a embed type, being either `rival` or `json` and a message url/id")
        types=['json','rival','bleed']
        if not message_url:
            return await util.send_error(ctx, f"please include a message url or id")
        # try:
        if message_url:
            if kind.lower()=='json':
                if message_url is None: return await ctx.reply(embed=discord.Embed(color=self.color, description=f"{self.bot.no} {ctx.author.mention}: **provide a message url**"))
                parts = [x for x in message_url.replace("/"," ").split() if len(x)]
                try: 
                    channel_id,message_id = [int(x) for x in parts[-2:]]
                except: 
                    try: 
                        channel_id = ctx.channel.id
                        message_id = message_url
                    except:
                        return await ctx.reply(embed=discord.Embed(color=self.color, description=f"{self.bot.no} {ctx.author.mention}: **invalid message url**"))
                guild = ctx.guild
                if len(parts) > 2:
                    if parts[-3].lower() == "@me":
                        guild = self.bot
                    else:
                        try: guild = self.bot.get_guild(int(parts[-3]))
                        except: pass
                if guild is None:
                    guild = ctx.guild if ctx.guild else self.bot
                channel = guild.get_channel(channel_id)
                if not channel: return await ctx.reply(color=self.color, embed=discord.Embed(description=f"{self.bot.no} {ctx.author.mention}: i couldn't find the channel connected to that id"))
                try: message = await channel.fetch_message(message_id)
                except: return await ctx.reply(embed=discord.Embed(color=self.color, description=f"{self.bot.no} {ctx.author.mention}: i couldn't find the message connected to that id"))
                if not len(message.embeds): return await ctx.reply(embed=discord.Embed(color=self.bot.color, description=f"{self.bot.no} {ctx.author.mention}: there are not embeds attached to that message"))
                tmp = tempfile.mkdtemp()
                for index,embed in enumerate(message.embeds):
                    name = "{}-{}-{}.json".format(channel_id,message_id,index)
                    fp = os.path.join(tmp,name)
                    m_dict = embed.to_dict()
                    try:
                        cc=hex(int(m_dict["color"]))
                        cc=str(cc)
                        cc=cc.strip('0x')
                        m_dict['color']=f'#{cc}'
                    except:
                        pass
                    try:
                        if m_dict.get("type"):
                            m_dict.pop("type")
                    except:
                        pass
                    try:
                        if m_dict['thumbnail']:
                            m_dict['thumbnail']=m_dict['thumbnail'].get('url')
                    except:
                        pass
                    try:
                        if m_dict['image']:
                            m_dict['image']=m_dict['image'].get("url")
                    except:
                        pass
                    try:
                        m_dict['message']=f'{message.content}'
                    except:
                        pass
                    try:
                        #json.dump(m_dict,open(fp,"w"),indent=2)
                        #await ctx.send(file=discord.File(fp=fp))
                        embed=json.dumps(m_dict)
                        try:
                            await ctx.reply(embed=discord.Embed(description=f"{self.bot.yes} {ctx.author.mention}: **successfully copied the embed code**\n\n```{discord.utils.escape_markdown(embed)}```", color=self.bot.color))
                        except:
                            await ctx.reply(embed=discord.Embed(description=f"{self.bot.yes} {ctx.author.mention}: **successfully copied the embed code**\n\n```{embed}```", color=self.bot.color))
                    except Exception as e:
                        pass
                shutil.rmtree(tmp,ignore_errors=True)
            else:
                if message_url is None: return await ctx.reply(embed=discord.Embed(color=self.color, description=f"{self.bot.no} {ctx.author.mention}: **provide a message url**"))
                parts = [x for x in message_url.replace("/"," ").split() if len(x)]
                try: 
                    channel_id,message_id = [int(x) for x in parts[-2:]]
                except: 
                    try: 
                        channel_id = ctx.channel.id
                        message_id = message_url
                    except:
                        return await ctx.reply(embed=discord.Embed(color=self.color, description=f"{self.bot.no} {ctx.author.mention}: **invalid message url**"))
                guild = ctx.guild
                if len(parts) > 2:
                    if parts[-3].lower() == "@me":
                        guild = self.bot
                    else:
                        try: guild = self.bot.get_guild(int(parts[-3]))
                        except: pass
                if guild is None:
                    guild = ctx.guild if ctx.guild else self.bot
                channel = guild.get_channel(channel_id)
                if not channel: return await ctx.reply(color=self.color, embed=discord.Embed(description=f"{self.bot.no} {ctx.author.mention}: i couldn't find the channel connected to that id"))
                try: message = await channel.fetch_message(message_id)
                except: return await ctx.reply(embed=discord.Embed(color=self.color, description=f"{self.bot.no} {ctx.author.mention}: i couldn't find the message connected to that id"))
                q=""
                if message.embeds:
                    e=message.embeds[0]
                    q="{embed}"
                    if e.color:
                        r=""
                        r+=f"color: {e.color}"
                        q+="{"+r+"}$v"
                    if e.description:
                        r=""
                        r+=f"description: {e.description}"
                        q+="{"+r+"}$v"
                    if e.title:
                        r=""
                        r+=f"title: {e.title}"
                        q+="{"+r+"}$v"
                    if e.footer:
                        r=""
                        if e.footer.text:
                            r+=f"footer: {e.footer.text}"
                        if e.footer.icon_url: r+=f" && icon: {e.footer.icon_url}"
                        q+="{"+r+"}$v"
                    if e.fields:
                        for f in e.fields:
                            r=""
                            r+=f"field: {f.name} && value: {f.value} && inline: {f.inline}"
                            q+="{"+r+"}$v"
                    if e.url:
                        r=""
                        r+=f"url: {e.url}"
                        q+="{"+r+"}$v"
                    if e.timestamp:
                        q+="{timestamp: true}$v"
                    if e.author:
                        r=""
                        if e.author.name:
                            r+=f"author: {e.author.name}"
                        if e.author.icon_url:
                            r+=f" && icon: {e.author.icon_url}"
                        if e.author.url:
                            r+=f" && url: {e.author.url}"
                        q+="{"+r+"}$v"
                    if e.image:
                        r=""
                        r+=f"image: {e.image.url}"
                        q+="{"+r+"}$v"
                    if e.thumbnail:
                        r=""
                        r+=f"thumbnail: {e.thumbnail.url}"
                        q+="{"+r+"}$v"
                if message.components:
                    for cp in message.components:
                        for child in cp.children:
                            if child.url and child.label or child.emoji:
                                r=""
                                if child.label:
                                    label=f"label: {child.label} && "
                                else:
                                    label=""
                                if child.emoji:
                                    emoji=f"emoji: {child.emoji} && "
                                r+=f"{label}{emoji}link: {child.url}"
                                q+="{"+r+"}$v"
                if len(q) > 1:
                    if "```" in q:
                        b=discord.utils.escape_markdown(q)
                    else:
                        b=f"```{discord.utils.escape_markdown(q)}```"
                    await ctx.reply(embed=discord.Embed(description=f"{self.bot.yes} {ctx.author.mention}: **successfully copied the embed code**\n\n{b}", color=self.bot.color))
        # except Exception as e:
        #     return await util.send_error(ctx, f"please give a type either `json` or `rival`\n{e}")


async def setup(bot):
    await bot.add_cog(embed(bot))
