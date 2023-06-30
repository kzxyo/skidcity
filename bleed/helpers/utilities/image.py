from io import BytesIO

from aiohttp import ClientSession  # circular import
from PIL import Image
from yarl import URL

from .process import async_executor


@async_executor()
def sample_colors(buffer: bytes) -> int:
    return int(
        "%02x%02x%02x"
        % (
            Image.open(BytesIO(buffer))
            .convert("RGBA")
            .resize((1, 1), resample=0)
            .getpixel((0, 0))
        )[:3],
        16,
    )


async def dominant(
    session: ClientSession,
    url: str,
) -> int:
    try:
        buffer = await session.request(
            "GET",
            URL(url),
        )
    except:
        return 0
    else:
        return await sample_colors(buffer)
