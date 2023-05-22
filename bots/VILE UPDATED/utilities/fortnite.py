from . import DL as http
from .utils import file
from io import BytesIO
from discord import File
from typing import List, Dict, Any, Optional


API_KEY = '395b534b-bb45-4ce8-9247-bf857bcf2001'


class Fortnite:
    def __init__(self, cosmetic: str = None):
        self.cosmetic = cosmetic


    @classmethod
    async def item_shop(self) -> File:
        return File(
            fp=BytesIO(await http.read(f"https://bot.fnbr.co/shop-image/fnbr-shop-{datetime.now().strftime('%-d-%-m-%Y')}.png")),
            filename='vile_itemshop.png'
        )

    
    async def cosmetic_info(self) -> Optional[Dict[str, Any]]:

        if not self.cosmetic:
            return None

        data = await http.get('https://fnbr.co/api/images', params={'search': self.cosmetic}, headers={'x-api-key': API_KEY})
        
        if not data['data']:
            return None

        return data['data'][0]