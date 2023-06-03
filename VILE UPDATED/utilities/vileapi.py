import traceback
from . import DL as http, utils, config
from typing import Dict, Optional, Any


API_KEY = config.authorization.vile_api


class VileAPI:
    def __init__(self, api_key: str = API_KEY) -> None:
        self.key = api_key

    
    async def user(self, user_id: int) -> Dict[str, Any]:
        return await http.get(
            'http://127.0.0.1:8443/user', 
            headers={'Authorization': self.key}, 
            params={'user_id': user_id}
        )


    async def names(self, user_id: int) -> Dict[str, Any]:
        return await http.get(
            'http://127.0.0.1:8443/names', 
            headers={'Authorization': self.key}, 
            params={'user_id': user_id}
        )


    async def tiktok(self, url: str) -> Dict[str, Any]:
        return await http.get(
            'http://127.0.0.1:8443/tiktok', 
            headers={'Authorization': self.key}, 
            params={'url': url}
        )


    async def youtube(self, url: str) -> Dict[str, Any]:
        return await http.get(
            'http://127.0.0.1:8443/youtube', 
            headers={'Authorization': self.key}, 
            params={'url': url}
        )


    async def images(self, query: str, safe: str = 'false') -> Dict[str, Any]:
        return await http.get(
            'http://127.0.0.1:8443/images', 
            headers={'Authorization': self.key}, 
            params={'query': query, 'safe': safe}
        )


    async def google(self, query: str, safe: str = 'false') -> Dict[str, Any]:
        return await http.get(
            'http://127.0.0.1:8443/google', 
            headers={'Authorization': self.key}, 
            params={'query': query, 'safe': safe}
        )


    async def tags(self) -> Dict[str, Any]:
        return await http.get(
            'http://127.0.0.1:8443/tags', 
            headers={'Authorization': self.key}
        )


    async def transparent(self, url: str) -> Dict[str, Any]:
        return await http.post(
            'http://127.0.0.1:8443/transparent', 
            headers={'Authorization': self.key}, 
            params={'url': url}
        )


    async def ocr(self, url: str) -> Dict[str, Any]:
        return await http.post(
            'http://127.0.0.1:8443/ocr', 
            headers={'Authorization': self.key}, 
            params={'url': url}
        )


    async def translate(self, text: str, target: str = 'english') -> Dict[str, Any]:
        return await http.get(
            'http://127.0.0.1:8443/transparent', 
            headers={'Authorization': self.key}, 
            params={'text': text, 'target': target}
        )


    async def hex(self, hex: str) -> Dict[str, Any]:
        return await http.get(
            'http://127.0.0.1:8443/hex', 
            headers={'Authorization': self.key}, 
            params={'hex': hex}
        )
