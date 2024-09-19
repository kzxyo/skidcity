from helpers.middleware import *

from aiohttp.web import (
    Application,
    HTTPException,
    HTTPFound,
    Request,
    Response,
    StreamResponse,
    _run_app
)

from aiohttp import (
    AsyncResolver,
    ClientSession,
    TCPConnector
)

from asyncio import (
    create_subprocess_shell,
    gather,
    sleep,
    wait_for
)

from bs4 import BeautifulSoup
from colorgram import extract as extract_color
from cryptography.fernet import Fernet
from discord import Asset, Color
from discord.utils import escape_markdown
from helpers import Router, Route, VileRedis
from httpx import AsyncClient
from io import BytesIO
from loguru import logger
from PIL import Image
from os import makedirs
from random import shuffle
from shutil import rmtree
from socket import AF_INET
from tuuid import tuuid
from typing import Any, Callable, Dict, List, Optional, Union
from typing_extensions import NoReturn
from xxhash import xxh3_64_digest as hash, xxh32_hexdigest as x3hash

import arrow
import asyncio
import aiohttp_jinja2
import jinja2
import orjson

    # <footer>
    #     <p>&copy; 2024 Vile Bot. All rights reserved.</p>
    #     <a href="//www.dmca.com/Protection/Status.aspx?ID=43e092e9-1963-4e9d-b46f-db3df884e23b" title="DMCA.com Protection Status" class="dmca-badge"> <img src ="https://images.dmca.com/Badges/dmca_protected_sml_120l.png?ID=43e092e9-1963-4e9d-b46f-db3df884e23b"  alt="DMCA.com Protection Status" /></a>  <script src="https://images.dmca.com/Badges/DMCABadgeHelper.min.js"> </script>
    # </footer>
    
    
async def eval_bash(script: str, decode: bool = False):
    process = await create_subprocess_shell(
        script,
        stdout=-1,
        stderr=-1
    )

    result, err = await process.communicate()

    if err:
        raise Exception(err.decode("utf-8"))
        
    return result.decode() if decode else result
    
    
async def get_dominant_color(
    redis: ...,
    source: Union[ Asset, str, bytes ]
) -> int:
    async def get_color(source: Union[ Asset, str, bytes ]) -> int:
        if isinstance(source, Asset):
            source = source.url
        
        if isinstance(source, bytes):
            resp = source
            
        else:
            try:
                async with ClientSession() as session:
                    async with session.get(source) as response:
                        resp = await response.read()
            
            except Exception as error:
                return 0
        
        image_hash = x3hash(resp)
            
        if (color := await redis.hget("dp:get_dominant_color", image_hash)):
            return color
                    
        try:
            image = Image.open(BytesIO(resp))
            image.thumbnail((100, 100))
            color = Color.from_rgb(*extract_color(image, 1)[0].rgb).value
            
        except Exception:
            return 0
            
        await redis.hset("dp:get_dominant_color", image_hash, color)
        
        return color
    
    return await wait_for(get_color(source=source), timeout=10)
    
    
async def _prompt(prompt: str, expert: str = "") -> str:
    prompt = prompt.replace("'", "\u2018").replace("'", "\u2019").replace('"', "\u201c").replace('"', "\u201d").replace("'", "\u0027").replace('"', "\u0022")

    async with ClientSession() as session:
        headers = {"accept": "*/*", "accept-language": "en-US,en;q=0.6", "content-type": "application/json", "cookie": "sessionId=567aa5e4-a01b-4f3e-b77b-1a175baacb55; intercom-device-id-jlmqxicb=67b29805-1ee5-4b56-96b1-005536e9f34a; __Secure-next-auth.session-token=eyJhbGciOiJkaXIiLCJlbmMiOiJBMjU2R0NNIn0..aBt7a4Nnsq8QFyPf.v6QbMNGWBnPybTE_NKF1VKJ1RinOwIV_DapDtO4JPSx9GSymMOMI_FxBkf7_A-7GXtTVZ8DGXUWQDrxpFcLi7hCQIdMVaoqoYOOmdHeFNVeIp1R1tRozMaQGMg4bNYcWu3ET2-JmMGdPU9OiYH_dUX15QtAanxKJ7vAB_HlJx00n2eu_HA0YGMdzfl20zJsftiqmowOLMM1T4Z9jmZVyN4CcLqyUFVQZJ5M-_Zhxf7oXWVzD36pVVGewX6cBsZLM4Iw3SHEJCd31b8UX3dS31aRwIrQwoVZbFmUElGrvNi0YjxKF_-v37LPfUoNzSHgDfv3Y9NPST1zbMw0Ao8jq6V_ydmgBkr7qn4h5ZRgROth_TcfVVnBJz7Dv-TZZrpMuV3avlq9F08TkpU7VCsJcApH2PDbXFCaDVGpEZRI7j2-Wup8s5cErJIEliy5CPUa1smzx0hwxSbScnCd-WKwgm20QI2xIP3Unv1tX-1YsjLrTyw.Kuj2uTjjHZdBzpaOKBnaaw; personalId=567aa5e4-a01b-4f3e-b77b-1a175baacb55; intercom-session-jlmqxicb=SkZRZnlkUVBIRm42OUhkdVdFcXJwZjU5M1o5Vk1PbCtZRUtQK3BKVkw2MjJWK0V3T3dsNmVZMzAvSDJ4OE1GVi0tSzZrUTZkaTFaR3A1UXp2QzJpTlZDZz09--6c97bef96363230490ce325ead039a73f27ccea7", "origin": "https://www.blackbox.ai", "referer": "https://www.blackbox.ai/chat", "sec-ch-ua": '"Brave";v="123", "Not:A-Brand";v="8", "Chromium";v="123"', "sec-ch-ua-mobile": "?0", "sec-ch-ua-platform": '"Windows"', "sec-fetch-dest": "empty", "sec-fetch-mode": "cors", "sec-fetch-site": "same-origin", "sec-gpc": "1", "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"}

        data = {"messages": [{"id": "UddxGeR", "content": prompt, "role": "user"}], "previewToken": None, "userId": "65d93bbc9ba56f00325371f2", "codeModelMode": True, "agentMode": {}, "trendingAgentMode": {"mode": True, "id": expert.lower()}, "isMicMode": False, "isChromeExt": False, "githubToken": None}

        async with session.post("https://www.blackbox.ai/api/chat", json=data, headers=headers) as response:
            response_data = await response.text()

            ret = "\n".join(response_data.splitlines()[2:]) if "Sources:" in response_data else response_data
            
            if "$@$" in ret:
                ret = ret[ret.index("$@$", 2)+3:]

            if "$~~~$" in ret:
                ret = ret[ret.index("$~~~$", 2)+5:]

            return ret


async def browse_images(redis, query: str, fetch_colors: bool = False) -> List[Dict[ str, Any ]]:
    
    async with AsyncClient() as client:
        soup = BeautifulSoup((await client.get("https://search.brave.com/images", params={"q": query})).text, "html.parser")
        ns = soup.findAll("div", class_="noscript-image")
        ret = []

        for ns in ns:
            await sleep(1e-3)
            
            image_src = ns.a.img['src']
            source_text = ns.find_next('div', class_='img-source').span.text.strip()
            title = ns.find_next('div', class_='img-title').text.strip()

            ret.append({"url": image_src, "domain": source_text, "title": title, "color": 0})

        if fetch_colors and "false" not in fetch_colors.lower():
            colors = await gather(*(get_dominant_color(redis, i["url"]) for i in ret))

            for index, image in enumerate(ret):
                await sleep(1e-3)
                image["color"] = int(colors[index])
    
        shuffle(ret)
        return ret
    

async def browse_search(query: str) -> List[Dict[ str, Any ]]:
    
    async with AsyncClient() as client:
        soup = BeautifulSoup((await client.get("https://search.brave.com/search", params={"q": query, "source": "desktop"})).text, "html.parser")
        ns = soup.findAll("div", {"data-type": "web"})
        ret = []

        for ns in ns:
            await sleep(1e-3)
            
            result_src = ns.find_next('cite', class_='snippet-url').span.text or "https://google.com"
            source_text = ns.find_next('div', class_='snippet-description').text or "No description"
            title = ns.find_next('div', class_='title').text or "Untitled"
            img = ns.find_next("img", class_="favicon").get("src", "")
            url = ns.find_next("a").get("href", "")
            subresults = []
            
            if (cluster := ns.find("div", class_="result-cluster")):
                for res in cluster.findAll("div", class_="snippet"):
                    await sleep(1e-3)
                    
                    result_src = ns.find_next('cite', class_='snippet-url').span.text or "https://google.com"
                    source_text = ns.find_next('div', class_='snippet-description').text or "No description"
                    title = ns.find_next('div', class_='title').text or "Untitled"
                    img = ns.find_next("img", class_="favicon").get("src", "")
                    url = ns.find_next("a").get("href", "")
                    
                    subresults.append({"domain": result_src.strip(), "description": source_text.strip(), "title": title.strip(), "url": url.strip()})
            
            ret.append({"domain": result_src.strip(), "description": source_text.strip(), "title": title.strip(), "image": img.strip(), "url": url.strip(), "subresults": subresults})

        shuffle(ret)
        return ret
        
        
HEADERS = {
    "Content-Security-Policy": "default-src 'none'; script-src 'self'; connect-src 'self'; img-src 'self'; style-src 'self'; frame-ancestors 'self'; form-action 'self';",
    "Strict-Transport-Security": "max-age=63070000; includeSubDomains; preload",
    "Referrer-Policy": "no-referrer"
}


async def set_headers(_, handler: Any) -> Callable:
    async def middleware(request: Request) -> StreamResponse:
        response = await handler(request)
        response._headers.update(HEADERS)
        return response

    return middleware
    
    
class WebServer(Router):
    def __init__(self: "WebServer") -> NoReturn:
        super().__init__()
        
        self.application = Application()
        self.redis = VileRedis()
        self.application.redis = self.redis
        
        self._fernet_key = ""
        self.address = ""
        self.fernet = Fernet(self._fernet_key)
        
        
    async def hkey_by_hval(self: "WebServer", hash_name: str, hval: Any) -> Optional[str]:
        hash_items = await self.redis.hgetall(hash_name)
        for key, value in hash_items.items():
            if value.decode() == hval:
                return key.decode()
            

    @Route(
        method = "GET",
        path   = "/ttx"
    )
    async def test(self: "WebServer", request: Request) -> StreamResponse:
        return Response(
            status=200,
            text=__import__("json").dumps(dict(request.headers), indent=4),
            content_type="application/json"
        )

        
    @Route(
        method = "GET",
        path   = "/"
    )
    async def home(self: "WebServer", request: Request) -> StreamResponse:
        return aiohttp_jinja2.render_template(
            "home.html", 
            request, 
            status=200,
            context={
                "guild_count": f"{int((await self.redis.get(b'guild_count')).decode()):,}",
                "user_count": f"{int((await self.redis.get(b'user_count')).decode()):,}",
        })


    @Route(
        method = "GET",
        path   = "/terms"
    )
    async def terms(self: "WebServer", request: Request) -> StreamResponse:
        return aiohttp_jinja2.render_template(
            "terms.html", 
            request, status=200
        )
        

    @Route(
        method = "GET",
        path   = "/privacy"
    )
    async def privacy(self: "WebServer", request: Request) -> StreamResponse:
        return aiohttp_jinja2.render_template(
            "privacy.html", 
            request, status=200
        )


    #@Route(
    #    method = "GET",
    #    path   = "/discord"
    #)
    #async def discord(self: "WebServer", request: Request) -> StreamResponse:
    #    raise HTTPFound("https://discord.gg/KsfkG3BZ4h")


    #@Route(
    #    method = "GET",
    #    path   = "/documentation"
    #)
    #async def documentation(self: "WebServer", request: Request) -> StreamResponse:
    #    raise HTTPFound("https://github.com/treyt3n/vile")


    #@Route(
    #    method = "GET",
    #    path   = "/invite"
    #)
    #async def invite(self: "WebServer", request: Request) -> StreamResponse:
    #    raise HTTPFound("https://discord.com/api/oauth2/authorize?client_id=1002261905613799527&permissions=8&scope=bot%20applications.commands")
        
        
    @Route(
        method = "GET",
        path   = "/ip"
    )
    async def ip(self: "WebServer", request: Request) -> StreamResponse:
        return Response(
            status=200,
            text=request.headers.get('Cf-Connecting-Ip', request.remote).replace(".", ";"),
            content_type="text/plain"
        )
    
    
    @Route(
        method = "POST",
        path   = "/api/browser/images"
    )
    async def api_browser_images(self: "WebServer", request: Request) -> StreamResponse:
        if not (query := await request.text()):
            return Response(
                status=400,
                text="""{"status": 400, "error": "400 Bad Request: `/api/browser/images?query=<str>&colors=[true/false]`"}""",
                content_type="application/json"
            )
            
        return Response(
            status=200,
            text=orjson.dumps(await browse_images(self.redis, query=query, fetch_colors=request.query.get("colors", "false"))).decode(),
            content_type="application/json"
        )
        
        
    @Route(
        method = "POST",
        path   = "/api/browser/search"
    )
    async def api_browser_search(self: "WebServer", request: Request) -> StreamResponse:
        if not (query := await request.text()):
            return Response(
                status=400,
                text="""{"status": 400, "error": "400 Bad Request: `/api/browser/search?query=<str>`"}""",
                content_type="application/json"
            )
        
        return Response(
            status=200,
            text=orjson.dumps(await browse_search(query=query)).decode(),
            content_type="application/json"
        )
        
    
    @Route(
        method = "POST",
        path   = "/api/prompt"
    )
    async def api_prompt(self: "WebServer", request: Request) -> StreamResponse:
        if not (message := await request.text()) or ((expert := request.query.get("expert", "")) and expert.lower() not in ("python", "html", "java", "javascript", "youtube", "pdf", "react", "elon", "android", "flutter", "steve", "nextjs", "angularjs", "swift", "mongodb", "pytorch", "xcode", "azure", "bitbucket", "digitalocean", "docker", "electron", "erlang", "fastapi", "firebase", "flask", "git", "gitlab", "go", "godot", "googlecloud", "heroku")):
            return Response(
                status=400,
                text="""{"status": 400, "error": "400 Bad Request: `/api/prompt-large?expert=[python/html/java/javascript/youtube/pdf/react/elon/android/flutter/steve/nextjs/angularjs/swift/mongodb/pytorch/xcode/azure/bitbucket/digitalocean/docker/electron/erlang/fastapi/firebase/flask/git/gitlab/go/godot/googlecloud/heroku] DATA=<str>`"}""",
                content_type="application/json"
            )
            
        return Response(text=await _prompt(prompt=message, expert=expert))
            
            
    @Route(
        method = "GET",
        path   = "/cache/{filename}"
    )
    async def cache(self: "WebServer", request: Request) -> StreamResponse:
        if not (filename := request.match_info.get("filename", None)):
            return Response(
                status=404,
                text="""{"status": 400, "error": "400 Bad Request: `/cache/<filename>`"}""",
                content_type="application/json"
            )
        
        try:
            with open(f"/root/.cache/vilebot/{filename}", "rb") as file:
                return Response(body=file.read())
            
        except FileNotFoundError:
            return Response(
                status=400,
                text="""{"status": 404, "error": "404 Not Found: File not found."}""",
                content_type="application/json"
            )
    
        
    @Route(
        method = "GET",
        path   = "/avatars/{user_id}"
    )
    async def avatars(self: "WebServer", request: Request) -> StreamResponse:
        if not (user_id := request.match_info.get("user_id", None)) or not user_id.isdigit():
            return Response(
                status=400,
                text="""{"status": 400, "error": "400 Bad Request: `/avatars/<user_id>`"}""",
                content_type="application/json"
            )

        time_ago_list = []

        async with self.session() as session:
            async with session.get(f"https://api.rival.rocks/avatars/{user_id}?format=json", headers={"api-key": ""}) as response:
                history_data = await response.json()

                if history_data is None:
                    return Response(text="null")

                avatar, avatars, _, name = history_data.values()

            time_agos = sorted(tuple(
                arrow.get(response.headers["Last-Modified"], "ddd, DD MMM YYYY HH:mm:ss [GMT]")
                for response in await asyncio.gather(*(
                session.request("HEAD", avatar) 
                for avatar in avatars
            ))
            ), reverse=True)

        from yattag import Doc
        doc, tag, text = Doc().tagtext()

        with tag("html"):
            with tag("head"):
                with tag("title"):
                    text("Avatar History")
        
                with tag("meta", name="theme-color", content="#171717"):
                    pass
                
                with tag("meta", property="og:title", content="Avatar History"):
                    pass
                
                with tag("meta", property="og:site_name", content=name):
                    pass
        
                with tag("meta", property="og:image", content=avatar):
                    pass
        
                with tag("style"):
                    text("""
                        body {
                            background-color: #171717;
                            justify-content: center;
                            align-items: center;
                            height: 100vh;
                            margin: 0;
                        }
                
                       .avatar-container {
                            position: relative;
                            display: inline-block;
                            margin: 10px;
                            margin-bottom: 40px;
                        }
                        
                       .avatar-img {
                            width: 150px;
                            height: 150px;
                            transition: transform 0.2s;
                        }
                        
                       .avatar-container:hover.avatar-img {
                            transform: scale(1.2);
                        }
                        
                       .avatar-text {
                            position: absolute;
                            top: 110%;
                            left: 50%;
                            transform: translateX(-50%);
                            background-color: transparent;
                            color: white;
                            padding: 10px;
                            font-size: 16px;
                            font-family: Arial, sans-serif;
                            white-space: nowrap;
                            opacity: 0;
                            transition: opacity 0.2s;
                            z-index: 2;
                        }
                        
                       .avatar-container:hover.avatar-text {
                            opacity: 1;
                        }
                    """)

        with tag("body"):
            for avatar, time_ago in zip(avatars, time_agos):
                with tag("div", klass="avatar-container"):
                    with tag("a", href=avatar):
                        with tag(
                            "img", klass="avatar-img", 
                            src=avatar, 
                            alt=time_ago.humanize(), 
                            decoding="async", 
                            style="color: transparent; display: inline; margin: 0 5px;"
                        ):
                            pass
                
                with tag("div", klass="avatar-text"):
                    text(time_ago.humanize())

        return Response(
            status=200,
            text=response,
            content_type="text/html"
        )

        
    @Route(
        method = "GET",
        path   = "/media/instagram"
    )
    async def media_instagram(self: "WebServer", request: Request) -> StreamResponse:
        if not (url := request.query.get("url", None)):
            return Response(
                status=400,
                text="""{"status": 400, "error": "400 Bad Request: `/media/instagram?url=<url>`"}""",
                content_type="application/json"
            )
        
        async with self.session().get(
            "https://api.rival.rocks/instagram/media", 
            params={
                "url": url,
                "api-key": ""
            }
        ) as response:
            return Response(
                status=200,
                text=await response.text(),
                content_type="application/json"
            )
            
            
    @Route(
        method = "GET",
        path   = "/media/youtube"
    )
    async def media_youtube(self: "WebServer", request: Request) -> StreamResponse:
        if not (url := request.query.get("url", None)):
            return Response(
                status=400,
                text="""{"status": 400, "error": "400 Bad Request: `/media/youtube?url=<url>`"}""",
                content_type="application/json"
            )
        
        async with self.session().get(
            f"https://api.rival.rocks/youtube", 
            params={
                "url": url,
                "api-key": ""
            }
        ) as response:
            return Response(
                status=200,
                text=await response.text(),
                content_type="application/json"
            )
            
            
    @Route(
        method = "GET",
        path   = "/api/fernet-key"
    )
    async def fernet_key(self: "WebServer", request: Request) -> StreamResponse:
        assert request.headers.get("Cf-Connecting-Ip", request.remote) == self.address
        return Response(
            status=200,
            text=f"{self._fernet_key}||{self.address}",
            content_type="text/plain"
        )
            
            
    @Route(
        method = "GET",
        path   = "/api/assistant/validate"
    )
    async def assistant_key_validation(self: "WebServer", request: Request) -> StreamResponse:
        if not (key := request.query.get("key", None)):
            return Response(
                status=400,
                text="""{"status": 400, "error": "400 Bad Request: `/assistant/validate?key=<key>`"}""",
                content_type="application/json"
            )

        active = key.encode() in await self.redis.hvals("assistant_keys")
        
        return Response(
            status=200 if active else 401,
            text="true" if active else "false",
            content_type="application/json"
        )

        
    @Route(
        method = "GET",
        path   = "/api/assistant/generate"
    )
    async def assistant_key_generation(self: "WebServer", request: Request) -> StreamResponse:
        assert request.headers.get("Cf-Connecting-Ip", request.remote) == self.address
        
        if not (user_id := request.query.get("user_id", None)):
            return Response(
                status=400,
                text="""{"status": 400, "error": "400 Bad Request: `/assistant/generate?user_id=<user_id>`"}""",
                content_type="application/json"
            )
            
        await self.redis.hset("assistant_keys", int(user_id), key:=f"{tuuid()[:8]}-{tuuid()[:8]}-{tuuid()[:8]}")
        
        return Response(
            status=200,
            text=key,
            content_type="application/json"
        )
        
        
    @Route(
        method = "GET",
        path   = "/api/assistant/regenerate"
    )
    async def assistant_key_regeneration(self: "WebServer", request: Request) -> StreamResponse:
        assert request.headers.get("Cf-Connecting-Ip", request.remote) == self.address
        
        if not (key := request.query.get("key", None)):
            return Response(
                status=400,
                text="""{"status": 400, "error": "400 Bad Request: `/assistant/regenerate?key=<key>`"}""",
                content_type="application/json"
            )
            
        if not (key.encode() in await self.redis.hvals("assistant_keys")):
            return Response(
                status=404,
                text="""{"status": 404, "error": "404 Not Found: That key does not exist."}""",
                content_type="application/json"
            )
            
        await self.redis.hset("assistant_keys", int(await self.hkey_by_hval("assistant_keys", key)), key:=f"{tuuid()[:8]}-{tuuid()[:8]}-{tuuid()[:8]}")
        
        return Response(
            status=200,
            text=key,
            content_type="application/json"
        )
        
    
    def session(self: "WebServer") -> ClientSession:
        return ClientSession(
            connector=TCPConnector(
                family=AF_INET,
                resolver=AsyncResolver(),
                limit=0,
                local_addr=None
            ),
            json_serialize=orjson.dumps
        )
        

    async def setup(self: "WebServer") -> NoReturn:
        await self.redis.initialize()
    
        aiohttp_jinja2.setup(
            self.application,
            loader=jinja2.FileSystemLoader("templates")
        )

        self.application.router.add_static(
            "/static/", 
            path="./static/", 
            name="static"
        )

        self.setup_routes(self.application)
        #self.application.middlewares.append(set_headers)
        
        for middleware in (
            Blacklist(),
            Ratelimit()
        ):
            middleware.setup(self.application)

        async with self.session().get("https://ipinfo.io/ip") as response:
            host = await response.text()

        await _run_app(
            host=host,
            port=8080,# 39812,
            app=self.application
        )


if __name__ == "__main__":
    makedirs("/root/.cache/vilebot", exist_ok=True)
    asyncio.run(WebServer().setup())