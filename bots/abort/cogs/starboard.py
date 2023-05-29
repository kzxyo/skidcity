import discord
from discord.ext import commands

# Configure the starboard channel ID and minimum number of stars required to appear on the starboard
STARBOARD_CHANNEL_ID = 1110989731614957659
MINIMUM_STARS = 1

@bot.event
async def on_raw_reaction_add(payload):
    # Check if the reaction is a star emoji and the message is not in the starboard channel
    if payload.emoji.name == "⭐" and payload.channel_id != STARBOARD_CHANNEL_ID:
        channel = await bot.fetch_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        starboard_channel = await bot.fetch_channel(STARBOARD_CHANNEL_ID)

        # Check if the message has already been starred on the starboard
        for reaction in message.reactions:
            if reaction.emoji == "⭐" and reaction.count >= MINIMUM_STARS:
                starred_message_id = None
                async for starred_message in starboard_channel.history():
                    if starred_message.embeds and starred_message.embeds[0].footer.text.startswith(f"⭐ {reaction.count} | {message.id}"):
                        starred_message_id = starred_message.id
                        break

                if starred_message_id:
                    starred_message = await starboard_channel.fetch_message(starred_message_id)
                    await starred_message.edit(embed=create_starboard_embed(message, reaction.count))
                else:
                    await starboard_channel.send(embed=create_starboard_embed(message, reaction.count))

                break

@bot.event
async def on_raw_reaction_remove(payload):
    # Check if the reaction is a star emoji and the message is not in the starboard channel
    if payload.emoji.name == "⭐" and payload.channel_id != STARBOARD_CHANNEL_ID:
        channel = await bot.fetch_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        starboard_channel = await bot.fetch_channel(STARBOARD_CHANNEL_ID)

        # Check if the message has already been starred on the starboard
        for reaction in message.reactions:
            if reaction.emoji == "⭐" and reaction.count < MINIMUM_STARS:
                async for starred_message in starboard_channel.history():
                    if starred_message.embeds and starred_message.embeds[0].footer.text.startswith(f"⭐ {reaction.count+1} | {message.id}"):
                        await starred_message.delete()
                        break

async def create_starboard_embed(message, star_count):
    author = message.author
    content = message.content
    timestamp = message.created_at
    avatar_url = author.avatar_url_as(static_format='png')

    embed = discord.Embed(
        description=content,
        timestamp=timestamp,
        color=discord.Color.gold()
    )
    embed.set_author(name=author.display_name, icon_url=avatar_url)
    embed.set_footer(text=f"⭐ {star_count} | {message.id}")

    if message.attachments:
        embed.set_image(url=message.attachments[0].url)

    return embed

class starboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

async def setup(bot):
    await bot.add_cog(lol(bot))