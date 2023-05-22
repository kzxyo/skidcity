from serpapi import GoogleSearch
import re,apipool, os
from apipool import ApiKey, ApiKeyManager
from modules import GetImage
import requests
#keys=["d48f6de7f9b90e9cbbbada29b6974c60cfa807866bbdc98e978ff912fd737495","dc0903d7836331ff17d754e9a911f76934bc324d9d1bff4f2215ef81b4db303d","2bc7bcbcebf8f8078c10cd7a8a5d8ced1c33cbdb9f0843bc6612bda46d184d53","68a6e4edc26c5d8898b85d7f9c660ba96951c76ee9129a83fc69aba55b6139a0","807029fe995002454a71205be65cb7a676b8c4e05311609899c3b85501c60792","dd0b9d307c0bc3bcc8591887a9682b2b4d7f48ea4a52c538cc28e491ba77c156","8a631ea8ef86c08d0be2c7cec51e247f6b11cfb867b8057a60cbcd2248881916","cf4632b77e91f79200164758f6bd66f4f9e6ed28a29ad651d2fe984802bfeb2c","7958fc119b95d3335b6fddcfcc4c6ddeee824c5b756d452aa9ce002c11021ce0","52325e766d85f7d92821ca4e3b7a7b5ae1f69fe17bd16504a8c4ad123e32739a","b45080bc2b1e4f6e6706c37ff7350aac11f96223e6b971f83feeaa532d10e4ae","a9555833f16381d748a7c08d4224845ab02b6ab1716d36749f7ff2907429d2c0","9a6c01815f04f8f65ba241bed0ff674cbf602faf7e2b50d0aef6d818089c03d6","ae59551c82b9aa24b8f666b9adae54deed3381a30190e5019ba94c318d7d0e2e","b0d49713aa41a82ad31a0b1f697b3f789e8f3227f6a6ba8f4aca260fc1542b08","d0a80f261d874340e43080954d63f2311da4446fb31dc38af17f6614b644d83a","46186dbde3c6a401ef6e690e2fead5ba84a39c93fc85f2c5216167a39b234b74"]
kkeys=['d48f6de7f9b90e9cbbbada29b6974c60cfa807866bbdc98e978ff912fd737495','dc0903d7836331ff17d754e9a911f76934bc324d9d1bff4f2215ef81b4db303d','2bc7bcbcebf8f8078c10cd7a8a5d8ced1c33cbdb9f0843bc6612bda46d184d53','68a6e4edc26c5d8898b85d7f9c660ba96951c76ee9129a83fc69aba55b6139a0','807029fe995002454a71205be65cb7a676b8c4e05311609899c3b85501c60792','dd0b9d307c0bc3bcc8591887a9682b2b4d7f48ea4a52c538cc28e491ba77c156','8a631ea8ef86c08d0be2c7cec51e247f6b11cfb867b8057a60cbcd2248881916','cf4632b77e91f79200164758f6bd66f4f9e6ed28a29ad651d2fe984802bfeb2c','7958fc119b95d3335b6fddcfcc4c6ddeee824c5b756d452aa9ce002c11021ce0','52325e766d85f7d92821ca4e3b7a7b5ae1f69fe17bd16504a8c4ad123e32739a','b45080bc2b1e4f6e6706c37ff7350aac11f96223e6b971f83feeaa532d10e4ae','a9555833f16381d748a7c08d4224845ab02b6ab1716d36749f7ff2907429d2c0','9a6c01815f04f8f65ba241bed0ff674cbf602faf7e2b50d0aef6d818089c03d6','ae59551c82b9aa24b8f666b9adae54deed3381a30190e5019ba94c318d7d0e2e','b0d49713aa41a82ad31a0b1f697b3f789e8f3227f6a6ba8f4aca260fc1542b08','d0a80f261d874340e43080954d63f2311da4446fb31dc38af17f6614b644d83a','46186dbde3c6a401ef6e690e2fead5ba84a39c93fc85f2c5216167a39b234b74']
kkeys=kkeys.copy()
transkeys=["XHjQW1Jnm9yF3B1wbDGD6Rs6","Vg59XAqaWQjayzhVEpsPEeUw", "iyK7stENZH4cGrWmKSn2QC56","KqFCZ53VxVBUthmvEy4CEyUk","NQPdUExZ3w8g27nz5yoyJ1DB","uCf8it5HvXFHbHg1HCXhQWGx","rph5yUcQxjNmogSsUqYHV6A1","aDvkyNGSRWYvQL4Eaz455c6q","RgY7XyjavJBAA4Zrzme7eZGZ","V7Mgi4anDfMp5PyrpZPqUSXY","ZDRoJRYhM1xag6iTHwZHCQMM","uYnF1DZcDzMkLva98FwiXvsP"]
emotekeys=["rph5yUcQxjNmogSsUqYHV6A1","aDvkyNGSRWYvQL4Eaz455c6q","RgY7XyjavJBAA4Zrzme7eZGZ","V7Mgi4anDfMp5PyrpZPqUSXY","ZDRoJRYhM1xag6iTHwZHCQMM","uYnF1DZcDzMkLva98FwiXvsP"]
start=0
async def search(query, nsfw=False):
	tries=len(keys)
	for i in range(tries):
		try:
			if nsfw:
				params = {"api_key": keys[i],"engine": "google","q": query,"google_domain": "google.com","gl": "us","hl": "en","num": "100","tbm": "isch","safe": "active"}
				search = GoogleSearch(params)
				print(tries)
				try:
					if search.get_dict()['error'] == "Your searches for the month are exhausted. You can upgrade plans on SerpApi.com website.":
						keys.remove(keys[i])
						print("removed 1 key")
				except Exception as e:
					print(e)
				print(tries)
				results = search.get_dict()['images_results']
				status=search.get_dict()["search_information"]["image_results_state"]
				if status=="Fully empty":
					return
				if "https://serpapi.com/search" not in results and results and results != None and results != "https://serpapi.com/search":
					return results
			else:
				params = {"api_key": keys[i],"engine": "google","q": query,"google_domain": "google.com","gl": "us","hl": "en","num": "100","tbm": "isch"}
				search = GoogleSearch(params)
				results = search.get_dict()['images_results']
				print(tries)
				try:
					if search.get_dict()['error'] == "Your searches for the month are exhausted. You can upgrade plans on SerpApi.com website.":
						keys.remove(keys[i])
						print("removed 1 key")
				except Exception as e:
					print(e)
				print(tries)
				status=search.get_dict()["search_information"]["image_results_state"]
				if status=="Fully empty":
					return
				if "https://serpapi.com/search" not in results and results and results != None and results != "https://serpapi.com/search":
					return results
		except KeyError as e:
			if i < tries - 1:
				continue
			else:
				raise
		break

async def transparent(image, url=False):
	tries=13
	if not url:
		for i in range(tries):
			response = requests.post(
			'https://api.remove.bg/v1.0/removebg',
			data={
				'image_url': image,
				'size': 'auto'
			},
			headers={'X-Api-Key': transkeys[i]},
			)
		if response.status_code == requests.codes.ok:
			with open('no-bg.png', 'wb') as out:
				out.write(response.content)
			return out
		else:
			print("Error:", response.status_code, response.text)
	else:
		for i in range(tries):
			file=await GetImage.download(image)
			response = requests.post(
			'https://api.remove.bg/v1.0/removebg',
			files={'image_file': open(file, 'rb')},
			data={'size': 'auto'},
			headers={'X-Api-Key': transkeys[i]},
			)
			if response.status_code == requests.codes.ok:
				with open('no-bg.png', 'wb') as out:
					out.write(response.content)
				os.remove(file)
				return out
			else:
				print("Error:", response.status_code, response.text)

async def trans(url=False):
	tries=6
	if not url:
		for i in range(tries):
			response = requests.post(
			'https://api.remove.bg/v1.0/removebg',
			data={
				'image_url': image,
				'size': 'auto'
			},
			headers={'X-Api-Key': emotekeys[i]},
			)
		if response.status_code == requests.codes.ok:
			with open('emoji.png', 'wb') as out:
				out.write(response.content)
			return out
		else:
			print("Error:", response.status_code, response.text)
	else:
		for i in range(tries):
			response = requests.post(
			'https://api.remove.bg/v1.0/removebg',
			files={'image_file': open("emoji.png", 'rb')},
			data={'size': 'auto'},
			headers={'X-Api-Key': emotekeys[i]},
			)
			if response.status_code == requests.codes.ok:
				with open('emoji.png', 'wb') as out:
					out.write(response.content)
				return out
			else:
				print("Error:", response.status_code, response.text)

