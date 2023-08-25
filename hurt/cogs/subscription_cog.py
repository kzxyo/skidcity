import discord
from discord.ext import commands
from datetime import datetime, timedelta
import random


class Database:
    def __init__(self):
        self.users = {}

    def insert(
        self, user_id, subscription_type, subscription_start_date, subscription_end_date
    ):
        self.users[user_id] = {
            "subscription_type": subscription_type,
            "subscription_start_date": subscription_start_date,
            "subscription_end_date": subscription_end_date,
        }


class SubscriptionCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.database = Database()

    @commands.command()
    async def subscribe(self, ctx, subscription_type):
        current_date = datetime.now()
        if subscription_type == "lifetime":
            subscription_end_date = None
        elif subscription_type == "monthly":
            subscription_end_date = current_date + timedelta(days=30)
        self.database.insert(
            ctx.author.id, subscription_type, current_date, subscription_end_date
        )
        await ctx.send("Subscribed successfully!")

    @commands.command()
    async def renew(self, ctx):
        user_id = ctx.author.id
        user = self.database.users.get(user_id)
        if user and user["subscription_type"] != "lifetime":
            renewal_successful = self.process_payment(
                user
            )  # Replace with actual payment logic
            if renewal_successful:
                new_end_date = user["subscription_end_date"] + timedelta(days=30)
                user["subscription_end_date"] = new_end_date
                await ctx.send("Your subscription has been renewed!")
            else:
                await ctx.send("Subscription renewal failed.")
        else:
            await ctx.send("You don't have a subscription to renew.")

    @commands.command()
    async def expiration(self, ctx):
        user_id = ctx.author.id
        expiration_date = self.get_subscription_expiration(user_id)
        if expiration_date:
            await ctx.send(f"Your subscription expires on: {expiration_date}")
        else:
            await ctx.send("You don't have an active subscription.")

    @commands.command()
    async def check_guild_subscription(self, ctx):
        owner_id = ctx.guild.owner_id
        expiration_date = self.get_subscription_expiration(owner_id)
        if expiration_date:
            await ctx.send(f"The guild's subscription expires on: {expiration_date}")
        else:
            await ctx.send("The guild doesn't have an active subscription.")

    def get_subscription_expiration(self, user_id):
        user = self.database.users.get(user_id)
        if user:
            return user["subscription_end_date"]
        return None

    def process_payment(self, user):
        # Simulate payment processing logic
        payment_success = random.choice(
            [True, False]
        )  # Randomly choose success or failure

        if payment_success:
            # Simulate successful payment by updating transaction ID
            user["transaction_id"] = f"TRANSACTION_{random.randint(1000, 9999)}"
            return True
        else:
            return False


async def setup(bot):
    await bot.add_cog(SubscriptionCog(bot))
