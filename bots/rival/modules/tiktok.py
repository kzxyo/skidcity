import requests
import urllib.parse
import urllib.request
import ssl

errortext="{'message': 'You have exceeded the DAILY quota for Requests on your current plan, BASIC"
async def tiktokalt(self, username):
	url = f"https://tiktok28.p.rapidapi.com/profile/{username}"

	querystring = {"schemaType":"1"}

	headers = {"X-RapidAPI-Key": "1e9a5af8edmsh342b5ff868255d3p173335jsnd4d7d4d1c566","X-RapidAPI-Host": "tiktok28.p.rapidapi.com"}

	response = requests.request("GET", url, headers=headers, params=querystring)
	return response.json()


async def tiktok(username):
	url = "https://tiktok-scraper2.p.rapidapi.com/user/info"

	querystring = {"user_name": f"{username}"}
	try:
		headers = {"X-RapidAPI-Key": "d4ab5ca0ccmsh7111580dad03a37p11b6d1jsne284e1371fd8","X-RapidAPI-Host": "tiktok-scraper2.p.rapidapi.com"}
		response = requests.request("GET", url, headers=headers, params=querystring)
		if response.json() and errortext not in response.json():
			return response.json()
	except:
		try:
			headers = {"X-RapidAPI-Key": "0c71fab5afmsh622ae7b8f342b5dp156652jsn9586792ecce5","X-RapidAPI-Host": "tiktok-scraper2.p.rapidapi.com"}
			response = requests.request("GET", url, headers=headers, params=querystring)
			if response.json() and errortext not in response.json():
				return response.json()
		except:
			try:
				response = requests.request("GET", url, headers=headers, params=querystring)
				if response.json() and errortext not in response.json():
					return response.json()
			except:
				try:
					url = "https://tiktok-scraper2.p.rapidapi.com/user/info"

					querystring = {"user_name":f"{username}"}

					headers = {"X-RapidAPI-Key": "1e9a5af8edmsh342b5ff868255d3p173335jsnd4d7d4d1c566","X-RapidAPI-Host": "tiktok-scraper2.p.rapidapi.com"}

					response = requests.request("GET", url, headers=headers, params=querystring)
					if response.json() and errortext not in response.json():
						return response.json()
				except:
					try:
						url = "https://tiktok-scraper2.p.rapidapi.com/user/info"

						querystring = {"user_name":f"{username}"}

						headers = {"X-RapidAPI-Key": "6b57a2c8d6mshc1c1fa35e6b9f34p16a0bdjsne99bc8cdcc58","X-RapidAPI-Host": "tiktok-scraper2.p.rapidapi.com"}

						response = requests.request("GET", url, headers=headers, params=querystring)
						if response.json() and errortext not in response.json():
							return response.json()
					except:
						print("more api keys needed")



async def tt(username):
	ssl._create_default_https_context = ssl._create_unverified_context

# Urlencode the URL
	url = urllib.parse.quote_plus("https://tiktok.com/@kitten")

# Create the query URL.
	query = "https://api.scraperbox.com/scrape"
	query += "?token=%s" % "3C72E7CD89FB9AD1EA573209A411667A"
	query += "&url=%s" % url

# Call the API.
	request = urllib.request.Request(query)
	raw_response = urllib.request.urlopen(request).read()
	html = raw_response.decode("utf-8")
	print(html)