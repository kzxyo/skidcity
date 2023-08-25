import discord
from discord.ext import commands
import openai


class ChatCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Set your API key here
        openai.api_key = "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"

    def get_gpt3_response(self, prompt):
        # Use the OpenAI GPT-3 API to get a response
        response = openai.Completion.create(
            engine="text-davinci-002",  # Use the appropriate engine here
            prompt=prompt,
            max_tokens=150,  # Adjust this based on how long you want the response to be
        )
        return response.choices[0].text.strip()

    @commands.command()
    async def chat(self, ctx, *, message):
        # Send the user message to the GPT-3 API for a response
        response = self.get_gpt3_response(message)

        # Create an embed with the response
        embed = discord.Embed(
            title="here's your response <:lean_wock:1136515976708497440>",
            description=response,
            color=discord.Color.purple(),
        )

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(ChatCog(bot))
