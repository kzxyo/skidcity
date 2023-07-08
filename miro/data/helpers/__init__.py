import discord

def embed(ctx, status, content):
    data = {
        "warning": {
            "emoji": "<:mirow:1117144157992009728>",
            "color": 0xfbe800,
            "text": "warning"
        },
        "deny": {
            "emoji": "<:mirodeny:1117144156507209829>",
            "color": 0xff4b50,
            "text": "deny"
        },
        "success": {
            "emoji": "<:miroapprove:1117144152363245638>",
            "color": 0x8fff77,
            "text": "success"
        }
    }
    try:
        return discord.Embed(description="%s %s: %s" % (data[status]["emoji"], ctx.author.mention, content), color=data[status]["color"])
    except:
        return discord.Embed(description="%s" % (content), color=0x8eabf7)