import discord, asyncio, aiohttp, bs4, discord, lxml

async def get_google_images(search_query, safe:bool):
	if safe == True:
		imgs = []
		titles = []
		headers = {
			'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:61.0) '
						  'Gecko/20100101 Firefox/61.0'),
			'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
		}
		for i in range(0, 100):
			#soup = BeautifulSoup(r.content, features="html.parser")
			#divs = str(soup.find_all('div', class_='entry grid-item'))
			#soup2 = BeautifulSoup(divs, features="html.parser")
			#images = soup2.find_all('img')
			url="http://images.google.com/search?q="+search_query+"&tbm=isch&sout=1&start=" + str(i)
			async with aiohttp.ClientSession() as cs:
				async with cs.get(url, headers=headers) as f:
					soup = bs4.BeautifulSoup(await f.text(), "html.parser")
			print(soup)
			for j in soup.find("div", {"id": "ires"}).find_all("a"):
				imgs.append(j.img['src'])
		return imgs
	else:
		imgs = []
		titles = []
		headers = {
			'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:61.0) '
						  'Gecko/20100101 Firefox/61.0'),
			'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
		}
		for i in range(0, 100):
			url="http://images.google.com/search?q="+search_query+"&tbm=isch&sout=1&start=" + str(i)
			async with aiohttp.ClientSession() as cs:
				async with cs.get(url, headers=headers) as f:
					soup = bs4.BeautifulSoup(await f.text(), "html.parser")
			print(soup)
			for j in soup.find("div", {"id": "ires"}).find_all("a"):
				imgs.append(j.img['src'])
		return imgs