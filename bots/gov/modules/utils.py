import discord, aiohttp, io


async def file(url: str, fn: str = None, filename: str = None):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as r:
            data = await r.read()

    fileName = ""
    if not fn and not filename:
        fileName = "image.png"
    elif not fn and filename:
        fileName = filename
    elif not filename and fn:
        fileName = fn
    elif filename and fn:
        return

    return discord.File(io.BytesIO(data), filename=fileName)
