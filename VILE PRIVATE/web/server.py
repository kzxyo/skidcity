from aiohttp.web import Application, Response, _run_app, Request, json_response
from datetime import datetime
import json, logging, discord
logger = logging.getLogger(__name__)
from discord.ext import commands, tasks


SOCKET_ADDRESS = {
    "host": "209.133.206.226",
    "port": 1337
}

class WebServer(commands.Cog):
    def __init__(self, bot: "VileBot") -> None:
        self.bot = bot
        self.uptime = datetime.now()
        self.app = Application()
        self.app.router.add_get("/", self.index)
        self.app.router.add_post("/test", self.test)


    async def cog_load(self):
        self.bot.loop.create_task(self.run())
        

    async def cog_unload(self):
        await self.shutdown()


    async def shutdown(self) -> None:
        await self.app.shutdown()
        await self.app.cleanup()
        

    async def run(self) -> None:
        logger.info(f"Starting WebServer on {':'.join(map(lambda v: str(v), SOCKET_ADDRESS.values()))}")
        await _run_app(
            self.app,
            **SOCKET_ADDRESS
        )

                
    @staticmethod
    async def index(request: Request) -> Response:
        return Response(text="Welcome to Vile's internal WebServer.", status=200)
        

    async def test(self, request: Request) -> Response:
        return Response(text="Your request was received.", status=200)

        
async def setup(bot: "VileBot") -> None:
    await bot.add_cog(WebServer(bot))
