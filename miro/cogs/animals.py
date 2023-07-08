import discord, requests, json, random
from discord.ext import commands
from modules import utils
session = requests.Session()

class animals(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = requests.Session()

    @commands.command(name = "lizard", description = "Return random lizard image",aliases=['liz'], usage = "lizard")
    @commands.cooldown(1, 3, commands.BucketType.guild)
    async def lizard(self, ctx):
        url = f"https://nekos.life/api/v2/img/lizard"
        resp = session.get(url)
        js = resp.json()
        embed = discord.Embed(color=0x4c5264)
        embed.set_image(url=js["url"])
        await ctx.reply(embed=embed)

    @commands.command(name = "goose", description = "Return random goose image",aliases=['gs'], usage = "goose")
    @commands.cooldown(1, 3, commands.BucketType.guild)
    async def goose(self, ctx):
        url = f"https://nekos.life/api/v2/img/goose"
        resp = session.get(url)
        js = resp.json()
        embed = discord.Embed(color=0x4c5264)
        embed.set_image(url=js["url"])
        await ctx.reply(embed=embed)



    @commands.command(name="lilpeep", description="Return random Lil Peep image", aliases=['peep'], usage="lilpeep")
    @commands.cooldown(1, 3, commands.BucketType.guild)
    async def lilpeep(self, ctx):
        base_url = "https://engar.party/api/lilpeep/raw/"
        try:
            random_number = random.randint(1, 220)
            url = base_url + str(random_number)
            resp = self.session.get(url)
            resp.raise_for_status()  # Raise an exception for non-2xx status codes

            embed = discord.Embed(color=0x4c5264)
            embed.add_field(name="Random Lil Peep Image", value=f"[Click here]({url})")
            embed.set_image(url=url)
            await ctx.reply(embed=embed)
        except (requests.RequestException, ValueError, KeyError) as e:
            await ctx.send(f"An error occurred: {e}")




    @commands.command(name = "cat", description = "Return random cat image",aliases=['catto'], usage = "cat")
    @commands.cooldown(1, 3, commands.BucketType.guild)
    async def cat(self, ctx):
        url = f"https://nekos.life/api/v2/img/meow"
        resp = session.get(url)
        js = resp.json()
        embed = discord.Embed(color=0x4c5264)
        embed.set_image(url=js["url"])
        await ctx.reply(embed=embed)

    @commands.command(name = "dog", description = "Return random dog image",aliases=['doggo'], usage = "dog")
    @commands.cooldown(1, 3, commands.BucketType.guild)
    async def dog(self, ctx):
        url = f"https://nekos.life/api/v2/img/woof"
        resp = session.get(url)
        js = resp.json()
        embed = discord.Embed(color=0x4c5264)
        embed.set_image(url=js["url"])
        await ctx.reply(embed=embed)

    @commands.command(name = "fox", description = "Return random fox image",aliases=['foxie'], usage = "fox")
    @commands.cooldown(1, 3, commands.BucketType.guild)
    async def fox(self, ctx):
        url = "https://randomfox.ca/floof/"
        response = requests.get(url)
        fox = response.json()

        embed = discord.Embed(color=0x4c5264)
        embed.set_image(url=fox["image"])
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(animals(bot))
