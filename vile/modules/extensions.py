import os

os.environ["JISHAKU_NO_UNDERSCORE"] = "True"


async def load(bot):

    await bot.load_extension("jishaku")
    folders = ["cogs", "events"]
    for folder in folders:
        for extension in os.listdir(folder):
            if "pycach" not in extension:
                await bot.load_extension(f"{folder}.{extension[:-3]}")
                print(f"loaded {folder}/{extension}")
