from typing import Iterable, Iterator, List, Tuple, Any
import re, aiohttp, urllib, asyncio
from bs4 import BeautifulSoup


def posnum(num: int) -> int: 
    if num < 0: 
        return - (num)
    else:
        return num


def get_every_nth_element(values: Iterable[Any], start_index: int, n: int) -> Iterator[Any]:
    return values[start_index::n]


class Google:
    def __init__(self) -> None:
        self.options = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
            'Content-Type': 'application/json'
        }
        self.cookies = None
        self.link_regex = re.compile(r'https?:\/\/(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&\/\/=]*(?:\.png|\.jpe?g|\.gif))')


    async def get_results(self, query: str, images: bool = False, safe: bool = False):

        encoded = urllib.parse.quote_plus(query, encoding='utf-8', errors='replace')

        async def get_html(url: str, encoded: str) -> str:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url + encoded, headers=self.options, cookies=self.cookies
                ) as resp:
                    self.cookies = resp.cookies
                    return await resp.text()

        if safe is True:
            encoded += '&safe=active'
			
        if images is False:
            url = 'https://www.google.com/search?q='
            text = await get_html(url, encoded)
			
        else:
            url = 'https://www.google.com/search?tbm=isch&q='
            text = await get_html(url, encoded)
			
        return await asyncio.to_thread(lambda: self.parser_image(text))


    async def get_titles(self, query: str, images: bool = True, safe: bool = False):

        encoded = urllib.parse.quote_plus(query, encoding='utf-8', errors='replace')

        async def get_html(url: str, encoded: str):
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url + encoded, headers=self.options, cookies=self.cookies
                ) as resp:
                    self.cookies = resp.cookies
                    return await resp.text()

        if safe is True:
            encoded += '&safe=active'
			
        if images is False:
            url = 'https://www.google.com/search?q='
            text = await get_html(url, encoded)
			
        else:
            titles = list()
            url = 'https://www.google.com/search?tbm=isch&q='
            text = await get_html(url, encoded)
			
            soup=BeautifulSoup(text, 'html.parser')
            divs = str(soup.find_all('div'))
            soup2 = BeautifulSoup(divs, features='html.parser')
            titles = soup2.find_all('h3')
			
            for title in titles:
                titles.append(title.text)
				
        return title
		

    async def combinator(self, data1: Iterable[Any], data2: Iterable[Any]) -> Tuple:
		
        a = list()
        b = list()
		
        for item in data1:
            a.append(data1)
			
        for data2 in data2:
            b.append(data2)
			
        merged = zip(a, b)
        google = list(merged)
        x = get_every_nth_element(google, 0, 2)
        y = get_every_nth_element(google, 1, 2)
        zipped = dict(zip(x,y))
		
        return zipped.items()


    def parser_image(self, html: str) -> List:
        return self.link_regex.findall(html)[7:]
