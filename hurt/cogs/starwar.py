import discord
from discord.ext import commands
import requests


class StarWars(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def people(self, ctx, *, query):
        url = f"https://swapi.dev/api/people/?search={query}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data["results"]:
                person = data["results"][0]
                name = person["name"]
                height = person["height"]
                mass = person["mass"]
                await ctx.send(f"Name: {name}\nHeight: {height}\nMass: {mass}")
            else:
                await ctx.send("No results found.")
        else:
            await ctx.send("An error occurred while fetching data.")

    @commands.command()
    async def starships(self, ctx, *, query):
        url = f"https://swapi.dev/api/starships/?search={query}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data["results"]:
                starship = data["results"][0]
                name = starship["name"]
                model = starship["model"]
                manufacturer = starship["manufacturer"]
                await ctx.send(
                    f"Name: {name}\nModel: {model}\nManufacturer: {manufacturer}"
                )
            else:
                await ctx.send("No results found.")
        else:
            await ctx.send("An error occurred while fetching data.")

    @commands.command()
    async def films(self, ctx, *, query):
        url = f"https://swapi.dev/api/films/?search={query}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data["results"]:
                film = data["results"][0]
                title = film["title"]
                episode_id = film["episode_id"]
                director = film["director"]
                await ctx.send(
                    f"Title: {title}\nEpisode ID: {episode_id}\nDirector: {director}"
                )
            else:
                await ctx.send("No results found.")
        else:
            await ctx.send("An error occurred while fetching data.")

    @commands.command()
    async def planets(self, ctx, *, query):
        url = f"https://swapi.dev/api/planets/?search={query}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data["results"]:
                planet = data["results"][0]
                name = planet["name"]
                climate = planet["climate"]
                terrain = planet["terrain"]
                await ctx.send(f"Name: {name}\nClimate: {climate}\nTerrain: {terrain}")
            else:
                await ctx.send("No results found.")
        else:
            await ctx.send("An error occurred while fetching data.")

    @commands.command()
    async def species(self, ctx, *, query):
        url = f"https://swapi.dev/api/species/?search={query}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data["results"]:
                specie = data["results"][0]
                name = specie["name"]
                classification = specie["classification"]
                language = specie["language"]
                await ctx.send(
                    f"Name: {name}\nClassification: {classification}\nLanguage: {language}"
                )
            else:
                await ctx.send("No results found.")
        else:
            await ctx.send("An error occurred while fetching data.")


async def setup(bot):
    await bot.add_cog(StarWars(bot))
