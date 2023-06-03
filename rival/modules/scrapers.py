import asyncio
import math
import re
import urllib
from typing import Tuple

from bs4 import BeautifulSoup


class ScrapingMixin:
    async def artist_top(self, ctx, period, artistname, datatype, name):
        """Scrape either top tracks or top albums from lastfm library page."""
        url = (
            f"https://last.fm/user/{name}/library/music/{artistname}/"
            f"+{datatype}?date_preset={self.period_http_format(period)}"
        )
        data = await self.fetch(ctx, url, handling="text")
        soup = BeautifulSoup(data, "html.parser")
        data = []
        try:
            chartlist = soup.find("tbody", {"data-playlisting-add-entries": ""})
        except ValueError:
            return None, []

        artist = {
            "image_url": soup.find("span", {"class": "library-header-image"})
            .find("img")
            .get("src")
            .replace("avatar70s", "avatar300s"),
            "formatted_name": soup.find("a", {"class": "library-header-crumb"}).text.strip(),
        }

        items = chartlist.findAll("tr", {"class": "chartlist-row"})
        for item in items:
            name = item.find("td", {"class": "chartlist-name"}).find("a").get("title")
            playcount = (
                item.find("span", {"class": "chartlist-count-bar-value"})
                .text.replace("scrobbles", "")
                .replace("scrobble", "")
                .strip()
            )
            data.append((name, int(playcount.replace(",", ""))))

        return artist, data

    async def lyrics_musixmatch(self, artistsong) -> Tuple[str, str]:
        artistsong = re.sub("[^a-zA-Z0-9 \n.]", "", artistsong)
        artistsong = re.sub(r"\s+", " ", artistsong).strip()
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Arch Linux; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0"
        }
        async with self.session.get(
            "https://musixmatch.com/search/{}".format(artistsong).replace(" ", "%20"),
            headers=headers,
        ) as resp:
            if resp.status == 200:
                result = await resp.text()
            else:
                return None, None
        soup = BeautifulSoup(result, "html.parser")
        songurl = soup.find("a", {"class": "title"})
        if songurl is None:
            return None, None
        url = "https://www.musixmatch.com" + songurl["href"]
        async with self.session.get(url, headers=headers) as resp:
            result = await resp.text()
        soup = BeautifulSoup(result, "html.parser")
        lyrics = soup.text.split('"body":"')
        lyrics = lyrics[0]
        songname = lyrics.split("|")[0]
        lyrics = lyrics.split('","language"')[0]
        try:
            lyrics = lyrics.split("languages")[1]
        except IndexError:
            return None, None
        lyrics = lyrics.split("Report")[0]
        lyrics = lyrics.replace("\\n", "\n")
        lyrics = lyrics.replace("\\", "")
        lyrics = lyrics.replace("&amp;", "&")
        lyrics = lyrics.replace("`", "'")
        lyrics = lyrics.strip()
        return lyrics, songname.strip()

    async def scrape_artist_image(self, artist, ctx):
        url = f"https://www.last.fm/music/{urllib.parse.quote_plus(artist)}/+images"
        data = await self.fetch(ctx, url, handling="text")

        soup = BeautifulSoup(data, "html.parser")
        if soup is None:
            return ""
        image = soup.find("img", {"class": "image-list-image"})
        if image is None:
            try:
                image = soup.find("li", {"class": "image-list-item-wrapper"}).find("a").find("img")
            except AttributeError:
                return ""
        return image["src"].replace("/avatar170s/", "/300x300/") if image else ""

    async def scrape_artists_for_chart(self, ctx, username, period, amount):
        period_format_map = {
            "7day": "LAST_7_DAYS",
            "1month": "LAST_30_DAYS",
            "3month": "LAST_90_DAYS",
            "6month": "LAST_180_DAYS",
            "12month": "LAST_365_DAYS",
            "overall": "ALL",
        }
        tasks = []
        url = f"https://www.last.fm/user/{username}/library/artists"
        for i in range(1, math.ceil(amount / 50) + 1):
            params = {"date_preset": period_format_map[period], "page": i}
            task = asyncio.ensure_future(self.fetch(ctx, url, params, handling="text"))
            tasks.append(task)

        responses = await asyncio.gather(*tasks)

        images = []
        for data in responses:
            if len(images) >= amount:
                break
            else:
                soup = BeautifulSoup(data, "html.parser")
                imagedivs = soup.findAll("td", {"class": "chartlist-image"})
                images += [
                    div.find("img")["src"].replace("/avatar70s/", "/300x300/") for div in imagedivs
                ]

        return images

    async def get_similar_artists(self, artistname, ctx):
        similar = []
        url = f"https://last.fm/music/{artistname}"
        data = await self.fetch(ctx, url, handling="text")
        soup = BeautifulSoup(data, "html.parser")
        for artist in soup.findAll("h3", {"class": "artist-similar-artists-sidebar-item-name"}):
            similar.append(artist.find("a").text)
        listeners = (
            soup.find("li", {"class": "header-metadata-tnew-item--listeners"}).find("abbr").text
        )
        return similar, listeners

    async def get_playcount_scraper(self, ctx, username, artistname, period):
        url = (
            f"https://last.fm/user/{username}/library/music/{artistname}"
            f"?date_preset={self.period_http_format(period)}"
        )
        data = await self.fetch(ctx, url, handling="text")
        soup = BeautifulSoup(data, "html.parser")
        divs = soup.findAll(class_="metadata-display")
        if not divs:
            return 0
        div = divs[0]
        plays = div.get_text()
        return int(plays.split(" ")[0].replace(",", ""))

    async def get_playcount_track_scraper(self, ctx, username, artistname, trackname, period):
        url = (
            f"https://last.fm/user/{username}/library/music/{artistname}/_/{trackname}"
            f"?date_preset={self.period_http_format(period)}"
        )
        data = await self.fetch(ctx, url, handling="text")
        soup = BeautifulSoup(data, "html.parser")
        divs = soup.findAll(class_="metadata-display")
        if not divs:
            return 0
        div = divs[0]
        plays = div.get_text()
        return int(plays.split(" ")[0].replace(",", ""))

    async def get_playcount_album_scraper(self, ctx, username, artistname, albumname, period):
        url = (
            f"https://last.fm/user/{username}/library/music/{artistname}/{albumname}"
            f"?date_preset={self.period_http_format(period)}"
        )
        data = await self.fetch(ctx, url, handling="text")
        soup = BeautifulSoup(data, "html.parser")
        divs = soup.findAll(class_="metadata-display")
        if not divs:
            return 0
        div = divs[0]
        plays = div.get_text()
        return int(plays.split(" ")[0].replace(",", ""))