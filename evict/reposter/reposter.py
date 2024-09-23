import io, aiohttp, yt_dlp, asyncio
import discord, re
from discord.ext import commands
from discord.ui import View, Button
from discord import Embed, File, Message
from collections import defaultdict
from bot.headers import Session

class Reposter:
    async def repost(self, bot: commands.Bot, message: discord.Message, url: str):
        if 'x.com' in url or 'twitter.com' in url:
            await self.repost_twitter(bot, message, url)
            return await message.delete()
        
        elif 'youtube.com' in url or 'youtu.be' in url:
            await self.repost_youtube(bot, message, url)
            return await message.delete()
        
        elif 'tiktok.com' in url:
            await self.repost_tiktok(bot, message, url)
            return await message.delete()
   
    def format_number(self, number: int) -> str:
        if number >= 1_000_000_000:
            return f"{number / 1_000_000_000:.2f}b"
        elif number >= 1_000_000:
            return f"{number / 1_000_000:.2f}m"
        elif number >= 1_000:
            return f"{number / 1_000:.2f}k"
        else:
            return str(number) 
        
    async def repost_twitter(self, bot: commands.Bot, message: discord.Message, url: str):
        await message.channel.typing()
        
        tweet_id_match = re.search(r'status/(\d+)', url)
        if not tweet_id_match: return
        file = None
        tweet = await bot.twitter.tweet_details(int(tweet_id_match.group(1)))
    
        
        if len(tweet.media.videos) >= 1: file = discord.File(fp=await self.read_file_from_url(tweet.media.videos[0].variants[1].url), filename='evict-twitter.mp4')
        
        tweet_content = tweet.rawContent
        tweet_content = re.sub(r'http\S+', '', tweet_content)
        
        view = discord.ui.View()
        view.add_item(discord.ui.Button(style=discord.ButtonStyle.link, label="View On 𝕏", url=tweet.url, emoji="<:twitter:1219531899106496574>"))
        embed = discord.Embed(color=0x1DA1F2, description=f"[**{tweet_content if len(tweet_content) >= 1 else 'No Caption'}**]({tweet.url})", timestamp=tweet.date)
        embed.set_author(name=f"{tweet.user.displayname} (@{tweet.user.username})", icon_url=tweet.user.profileImageUrl, url=tweet.user.url)
        embed.set_footer(icon_url='https://www.iconpacks.net/icons/2/free-twitter-logo-icon-2429-thumb.png', text="❤️ {}  🔁 {} ∙ Requested by: {}".format(tweet.likeCount, tweet.retweetCount, message.author))
        
        if len(tweet.media.photos) >= 1: embed.set_image(url=tweet.media.photos[0].url)
        
        return await message.channel.send(embed=embed, file=file, view=view) if file is not None else await message.channel.send(embed=embed, view=view)
    
    async def repost_youtube(self, bot: commands.Bot, message: discord.Message, url: str):
        await message.channel.typing()
        ydl_opts = {
            'outtmpl': 'youtube.mp4',
            'noplaylist': True,
            'playlist_items': '0',
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
        
        channel = yt_dlp.YoutubeDL({'playlist_items': '0'}).extract_info(info['uploader_url'])

        if info['age_limit'] != 0: return await message.channel.send(embed=discord.Embed(color=bot.color, description=f"{message.author.mention}: I can't repost possibly **sensitive** videos."))
        
        views = self.format_number(info['view_count'])
        likes = self.format_number(info['like_count'])

        embed = discord.Embed(color=bot.color, description=f"[**{info['title'][:100] + '...' if len(info['title']) > 150 else info['title']}**]({info['webpage_url']})")
        formats = [f for f in info['formats'] if f['ext'] is not None and f['ext'] == 'mp4' and f['vcodec'] != 'none' and f['acodec'] != 'none']
        
        if len(formats) == 0: return print('Could not find any formats')
        
        file = discord.File(fp=await self.read_file_from_url(formats[0]['url']), filename='evict-youtube.mp4')
        embed.set_author(name=f"{info['uploader']} ({info['uploader_id']})", url=info['uploader_url'], icon_url=channel['thumbnails'][-1]['url'])
        embed.set_footer(icon_url=message.author.display_avatar.url, text=f"Requested by {message.author} ﹒ Views: {views} ﹒Likes: {likes}")
        view = discord.ui.View()
        view.add_item(discord.ui.Button(style=discord.ButtonStyle.link, label="View On YouTube", url=info['webpage_url'], emoji="<:youtube:1219530840070160384>"))
        return await message.channel.send(embed=embed, file=file, view=view)
    
    async def repost_tiktok(self, bot: commands.Bot, message: discord.Message, url: str):

        session = Session()
      
        locks = defaultdict(asyncio.Lock)

        async with locks[message.guild.id]:  
         
         url = message.content[len("evict")+1:]
         try: 
          await message.delete()
         except: 
          pass
         
         async with message.channel.typing():       
          x = await session.get_json("https://tikwm.com/api/", params={"url": url}) 
          if x['data'].get("images"):
            embeds = []
            for img in x['data']['images']:
              embed = Embed(
                color=self.bot.color,
                description=f"[**Tiktok**]({url}) requested by {message.author}"
              )\
              .set_author(
                name=f"@{x['data']['author']['unique_id']}",
                icon_url=x["data"]["author"]["avatar"],
                url=url
              )\
              .set_footer(
                text=f"❤️ {x['data']['digg_count']:,}  💬 {x['data']['comment_count']:,} | {x['data']['images'].index(img)+1}/{len(x['data']['images'])}"
              )\
              .set_image(url=img)    
            
            embeds.append(embed)
            ctx = await self.bot.get_context(message)
            return await ctx.paginate(embeds)
          else:
            video = x["data"]["play"]
            file = File(fp=await session.getbyte(video), filename="evicttiktok.mp4")
            embed = Embed(
              color=bot.color,
              description=f"[{x['data']['title']}]({url})" if x['data']['title'] else ""
            )\
            .set_author(
              name=f"@{x['data']['author']['unique_id']}",
              icon_url=x["data"]["author"]["avatar"]
            )
            x = x["data"]

            embed.set_footer(
              text=f"❤️ {x['digg_count']:,}  💬 {x['comment_count']:,}  🔗 {x['share_count']:,}  👀 {x['play_count']:,} | {message.author}"
            )
            await message.channel.send(embed=embed, file=file)
    
    async def read_file_from_url(self, url: str):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    return None
                return io.BytesIO(await resp.read())