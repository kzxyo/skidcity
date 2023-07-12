import random
import string
import discord
from typing import List
from PIL import Image
from .utils import async_executor
import aiohttp
import io
from math import sqrt
import asyncio

def api_key_generator(user_name: str) -> str:
    random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    return f"{user_name}:{random_string}"

@async_executor()
def _collage_open(image: io.BytesIO):
    image = (
        Image.open(image)
        .convert("RGBA")
        .resize(
            (
                256,
                256,
            )
        )
    )
    return image


async def read(image: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(image) as response:
            return await _collage_open(io.BytesIO(await response.read()))
        
async def paste(image: Image, x: int, y: int, background: Image):
    background.paste(
        image,
        (
            x * 256,
            y * 256,
        ),
    )

async def generate_collage(images: List[str]):
    tasks = list()
    for image in images:
        tasks.append(read(image))

    images = [image for image in await asyncio.gather(*tasks) if image]
    if not images:
        return "Could not generate images."

    rows = int(sqrt(len(images)))
    columns = (len(images) + rows - 1) // rows

    background = Image.new(
        "RGBA",
        (
            columns * 256,
            rows * 256,
        ),
    )
    tasks = list()
    for i, image in enumerate(images):
        tasks.append(paste(image, i % columns, i // columns, background))
    await asyncio.gather(*tasks)

    buffer = io.BytesIO()
    background.save(
        buffer,
        format="png",
    )
    buffer.seek(0)

    background.close()
    for image in images:
        image.close()

    return discord.File(
        buffer,
        filename="collage.png",
    )