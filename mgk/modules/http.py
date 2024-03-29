import httpx

async def get(url, params=None, headers=None):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params, headers=headers)
            if response.status_code == 200:
                return response.json()
            else:
                return response.status_code
        except httpx.RequestError as e:
            return e
