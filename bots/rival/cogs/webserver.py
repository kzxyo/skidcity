import os,json,aiohttp,socket,orjson
import ssl

import aiohttp_cors
from aiohttp import web
from discord.ext import commands, tasks
from prometheus_async import aio
from fake_headers import Headers

from modules import log,cache

import logging
logger = logging.getLogger(__name__)

USE_HTTPS = os.environ.get("WEBSERVER_USE_HTTPS", "no")
HOST = os.environ.get("WEBSERVER_HOSTNAME")
PORT = int(os.environ.get("WEBSERVER_PORT", 0))
SSL_CERT = os.environ.get("WEBSERVER_SSL_CERT")
SSL_KEY = os.environ.get("WEBSERVER_SSL_KEY")

class WebServer(commands.Cog):
    """Internal web server to provice realtime statistics to the website"""

    def __init__(self, bot):
        self.bot = bot
        self.app = web.Application()
        self.cached = {
            "guilds": 0,
            "users": 0,
            "commands": 0,
            "donators": [],
        }
        self.cached_command_list = []
        self.app.router.add_get("/", self.index)
        self.app.router.add_get("/ping", self.ping_handler)
        self.app.router.add_get("/stats", self.website_statistics)
        self.app.router.add_get("/docs", self.command_list)
        self.app.router.add_get("/donators", self.donator_list)
#        self.app.router.add_get("/users", self.user_list)
        self.app.router.add_get("/tiktok", self.tiktok)
        self.app.router.add_get('/tiktoklookup', self.tiktok_lookup)
        self.app.router.add_get("/lookup", self.new_user)
        self.app.router.add_get('/tags', self.tag_list)
        self.app.router.add_get("/cluster", aio.web.server_stats)
        # Configure default CORS settings.
        self.cors = aiohttp_cors.setup(
            self.app,
            defaults={
                "*": aiohttp_cors.ResourceOptions(
                    allow_credentials=True,
                    expose_headers="*",
                    allow_headers="*",
                )
            },
        )

        # Configure CORS on all routes.
        for route in list(self.app.router.routes()):
            self.cors.add(route)

        # https
        if USE_HTTPS == "yes":
            self.ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            self.ssl_context.load_cert_chain(SSL_CERT, SSL_KEY)
        else:
            self.ssl_context = None

    async def cog_load(self):
        self.cache_stats.start()
        self.cached_command_list = self.generate_command_list()
        self.bot.loop.create_task(self.run())

    async def cog_unload(self):
        self.cache_stats.cancel()
        await self.shutdown()

    async def tiktok_lookup(self, request):
        apikey=request.rel_url.query.get('key')
        d={}
        if apikey:
            if not apikey in self.bot.cache.apikeys:
                d['status']='Fail'
                d['Error']="API Key not authorized"
                return web.Response(text=json.dumps(d), status=500)
        else:
            if request.remote != "154.12.248.219":
                d['status']='Fail'
                d['Error']="API Key Not Provided via `?key={apikey}` url parameter" 
                return web.Response(text=json.dumps(d), status=500)
        s={}
        user=request.rel_url.query.get('user')
        if not user:
            s['status']='Fail'
            s['Error']='No User Provided'
            return web.Response(text=json.dumps(s), status=500)
        header = Headers(headers=False)
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://www.tiktok.com/node/share/user/@{user}?aid=1988", headers={'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'}) as r:
                d=await r.json(content_type=None)
        #async with aiohttp.ClientSession(headers={'fp':q['verifyConfig'].get("fp"), 'User-Agent':"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36"}) as sesh:
            #async with sesh.get(f"https://www.tiktok.com/node/share/user/@{user}?aid=1988", headers={'fp':q['verifyConfig'].get("fp"), 'User-Agent':"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36"}) as k:
               # d=await k.json(content_type=None)
        return web.Response(text=json.dumps(d), status=200)

    async def tiktok(self,request):
        apikey=request.rel_url.query.get('key')
        if request.remote not in self.bot.cache.api_access_address:
            self.bot.cache.api_access_address.append(request.remote)
        if apikey not in self.bot.cache.api_audit:
            self.bot.cache.api_audit[apikey]=[]
        if request.remote not in self.bot.cache.api_audit[apikey]:
            if len(self.bot.cache.api_audit[apikey]) > 1:
                response_object = {'status':'failed','error':'IP Address Unauthorized for API Key Use'}
                return web.Response(text=json.dumps(response_object), status=500)
            else:
                self.bot.cache.api_audit[apikey].append(request.remote)
        d={}
        #apikey=request.rel_url.query.get('key')
        if apikey:
            if not apikey in self.bot.cache.apikeys:
                d['status']='failed'
                d['error']="API Key not authorized"
                return web.Response(text=json.dumps(d), status=500)
        else:
            if request.remote != "154.12.248.219":
                d['status']='failed'
                d['error']="API Key Not Provided via `?key={apikey}` url parameter"
                return web.Response(text=json.dumps(d), status=500)

        if apikey not in self.bot.cache.api_ratelimit:
            self.bot.cache.api_ratelimit[apikey]=0
        self.bot.cache.api_ratelimit[apikey]+=1

        # try:
        #     if int(self.bot.cache.api_ratelimit[apikey]) > 5:
        #         response_object = {'status':'failed','error':'Ratelimit try again in 1 second'}
        #         return web.Response(text=json.dumps(response_object), status=500)
        # except Exception as e:
        #     print(f'Ratelimit Exception: {e}')

        d={}
        apikey=request.rel_url.query.get('key')
        user_id=request.rel_url.query.get('user')
        guild_id=request.rel_url.query.get('guild')
        if not guild_id:
            d['status']='Fail'
            d['Error']="Guild Not Provided via `guild={id}` parameter"
        if not user_id:
            d['status']='Fail'
            d['Error']="User Not Provided via `user={id}` parameter"
        if apikey:
            if not apikey in self.bot.cache.apikeys:
                d['status']='Fail'
                d['Error']="API Key not authorized"
                return web.Response(text=json.dumps(d), status=500)
        else:
            if request.remote != "154.12.248.219":
                d['status']='Fail'
                d['Error']="API Key Not Provided via `?key={apikey}` url parameter" 
                return web.Response(text=json.dumps(d), status=500)
        url=request.rel_url.query.get('url')
        async with aiohttp.ClientSession(cookie_jar=aiohttp.CookieJar(unsafe=True),timeout=aiohttp.ClientTimeout(total=30),connector=aiohttp.TCPConnector(verify_ssl=False,family=socket.AF_INET, keepalive_timeout=30, limit=500, limit_per_host=100, ttl_dns_cache=3600),headers={"CF-Access-Client-Id": "5fad336113f621b1e4a6f5be8f4e1481.access","CF-Access-Client-Secret": "95c00e3196f1dfbebd0f5247e09a7a118ec6403b0c2957ce6ed963694c1e262f"}) as session:
            async with session.post("https://dev.melaniebot.gg/api/tiktok/post", json={"url": url, 'user_id': user_id, 'guild_id': guild_id}) as r:
                return web.Response(text=json.dumps(await r.json()), status=200)

    async def tag_list(self, request):
        apikey=request.rel_url.query.get('key')
        if request.remote not in self.bot.cache.api_access_address:
            self.bot.cache.api_access_address.append(request.remote)
        if apikey not in self.bot.cache.api_audit:
            self.bot.cache.api_audit[apikey]=[]
        if request.remote not in self.bot.cache.api_audit[apikey]:
            if len(self.bot.cache.api_audit[apikey]) > 1:
                response_object = {'status':'failed','error':'IP Address Unauthorized for API Key Use'}
                return web.Response(text=json.dumps(response_object), status=500)
            else:
                self.bot.cache.api_audit[apikey].append(request.remote)
        d={}
        #apikey=request.rel_url.query.get('key')
        if apikey:
            if not apikey in self.bot.cache.apikeys:
                d['status']='failed'
                d['error']="API Key not authorized"
                return web.Response(text=json.dumps(d), status=500)
        else:
            if request.remote != "154.12.248.219":
                d['status']='failed'
                d['error']="API Key Not Provided via `?key={apikey}` url parameter"
                return web.Response(text=json.dumps(d), status=500)

        if apikey not in self.bot.cache.api_ratelimit:
            self.bot.cache.api_ratelimit[apikey]=0
        self.bot.cache.api_ratelimit[apikey]+=1

        # try:
        #     if int(self.bot.cache.api_ratelimit[apikey]) > 5:
        #         response_object = {'status':'failed','error':'Ratelimit try again in 1 second'}
        #         return web.Response(text=json.dumps(response_object), status=500)
        # except Exception as e:
        #     print(f'Ratelimit Exception: {e}')

        if apikey:
            if not apikey in self.bot.cache.apikeys:
                d['status']='Fail'
                d['Error']="API Key not authorized"
                return web.Response(text=json.dumps(d), status=500)
        else:
            if request.remote != "154.12.248.219":
                d['status']='Fail'
                d['Error']="API Key Not Provided via `?key={apikey}` url parameter" 
                return web.Response(text=json.dumps(d), status=500)
        cc=await self.bot.redis.get("tags1")
        cf=await self.bot.redis.get("tags2")
        cd=await self.bot.redis.get("tags3")
        cg=await self.bot.redis.get("tagsblame")
        #cv=await self.bot.redis.get("tags0")
        #cs=await self.bot.redis.get("tags4")
        #ck=await self.bot.redis.get("tags5")
        if cg:
            tags=orjson.loads(cc) | orjson.loads(cf) | orjson.loads(cd) | orjson.loads(cg)
        else:
            tags=orjson.loads(cc) | orjson.loads(cf) | orjson.loads(cd)
        s=[]
        d['status']="Success"
        d['tags']=tags
        return web.Response(text=json.dumps(d),status=200)

    async def new_user(self,request):
        apikey=request.rel_url.query.get('key')
        if 65 not in self.bot.cache.api_access_address:
            self.bot.cache.api_access_address.append(request.remote)
        if apikey not in self.bot.cache.api_audit:
            self.bot.cache.api_audit[apikey]=[]
        if request.remote not in self.bot.cache.api_audit[apikey]:
            if len(self.bot.cache.api_audit[apikey]) > 1:
                response_object = {'status':'failed','error':'IP Address Unauthorized for API Key Use'}
                return web.Response(text=json.dumps(response_object), status=500)
            else:
                self.bot.cache.api_audit[apikey].append(request.remote)
        d={}
        #apikey=request.rel_url.query.get('key')
        if apikey:
            if not apikey in self.bot.cache.apikeys:
                d['status']='failed'
                d['error']="API Key not authorized"
                return web.Response(text=json.dumps(d), status=500)
        else:
            if request.remote != "154.12.248.219":
                d['status']='failed'
                d['error']="API Key Not Provided via `?key={apikey}` url parameter"
                return web.Response(text=json.dumps(d), status=500)

        if apikey not in self.bot.cache.api_ratelimit:
            self.bot.cache.api_ratelimit[apikey]=0
        self.bot.cache.api_ratelimit[apikey]+=1

        s=[]
        d['status']="Success"
        try:
            ## happy path where name is set
            user = request.rel_url.query.get('id')
            ## Process our new user
            async with aiohttp.ClientSession() as qqq:
                async with qqq.get(f"https://japi.rest/discord/v1/user/{user}") as r:
                    p=await r.json()
            try:
                p.pop("cached")
                p.pop("cache_expiry")
            except:
                pass
            try:
                d['source']='https://rival.rocks'
                try:
                    guilds=[]
                    bb=''.join(b for b in p['public_flags_array'])
                    if "boost" not in bb.lower():
                        u=await self.bot.fetch_user(user)
                        for g in u.mutual_guilds:
                            vanity=str(await d.vanity_invite())
                            if vanity:
                                v=vanity
                            else:
                                v="None"
                            guilds.append({'name':d.name,'owner_id':d.owner.id,'owner_tag':str(d.owner),'member_count':len(d.members),'vanity':v,'permissions':str(g.get_member(u).permissions)})
                            if u in g.premium_subscribers:
                                p=g.get_member(u)
                                s.append(p.premium_since)
                    else:
                        u=await self.bot.fetch_user(user)
                        for g in u.mutual_guilds:
                            d=self.bot.get_guild(g.id)
                            if d:
                                vanity=str(await g.vanity_invite())
                                if vanity:
                                    v=vanity
                                else:
                                    v="None"
                                guilds.append({'name':d.name,'owner_id':d.owner.id,'owner_tag':str(d.owner),'member_count':len(d.members),'vanity':v,'permissions':str(g.get_member(u).permissions)})
                        if s:
                            s.sort()
                            if s[0] < await util.datetime_delta(1):
                                p['public_flags_array'].append('Booster_1')
                            elif s[0] < await util.datetime_timedelta(2):
                                p['public_flags_array'].appemd('Booster_2')
                            elif s[0] < await util.datetime_delta(3):
                                p['public_flags_array'].append('Booster_3')
                            elif s[0] < await util.datetime_delta(6):
                                p['public_flags_array'].append('Booster_6')
                            elif s[0] < await util.datetime_delta(9):
                                p['public_flags_array'].append('Booster_9')
                            elif s[0] < await util.datetime_delta(12):
                                p['public_flags_array'].append('Booster_12')
                            elif s[0] < await util.datetime_delta(15):
                                p['public_flags_array'].append('Booster_15')
                            elif s[0] < await util.datetime_delta(18):
                                p['public_flags_array'].append('Booster_18')
                            elif s[0] < await util.datetime_delta(21):
                                p['public_flags_array'].append('Booster_21')
                            elif s[0] < await util.datetime_delta(24):
                                p['public_flags_array'].append('Booster_24')
                            else:
                                p['public_flags_array'].append('Booster_1')
                    if "nitro" not in bb.lower():
                        if u.display_avatar.is_animated() or u.banner:
                            p['public_flags_array'].append("NITRO")
                except Exception as e:
                    print(e)
                    pass
                for key,value in p.items():
                    d[key]=value
                d['guilds']=guilds
                # data = await self.bot.db.execute("SELECT name, ts FROM namehistory WHERE user_id = %s ORDER BY ts DESC", user)
                # q=[]
                # if data:
                #     for name, ts in data:
                #         q.append({'name':name,'timestamp':f"{ts}"})
                # d['names']=q
            except Exception as e:
                d['message']="Unknown User"
                d['status']='Fail'


            response_obj = { 'status' : 'success' }
            ## return a success json response with status code 200 i.e. 'OK'
            return web.Response(text=json.dumps(d), status=200)
        except Exception as e:
            ## Bad path where name is not set
            response_obj = { 'status' : 'failed', 'reason': str(e) }
            ## return failed with a status code of 500 i.e. 'Server Error'
            return web.Response(text=json.dumps(response_obj), status=500)

    @tasks.loop(minutes=1)
    async def cache_stats(self):
        self.cached["commands"] = int(
            await self.bot.db.execute("SELECT SUM(uses) FROM command_usage", one_value=True)
        )
        mc=int(await self.bot.redis.get("membercount1"))+int(await self.bot.redis.get("membercount2"))+int(await self.bot.redis.get("membercount3"))#+int(await self.bot.redis.get(membercount0))+int(await self.bot.redis.get("membercount4"))+int(await self.bot.redis.get("membercount5"))
        guilds=int(await self.bot.redis.get("guilds1"))+int(await self.bot.redis.get("guilds2"))+int(await self.bot.redis.get("guilds3"))#+int(await self.bot.redis.get("guilds0"))+int(await self.bot.redis.get("guilds4"))+int(await self.bot.redis.get("guilds5"))
        self.cached["guilds"] = guilds
        self.cached["users"] = mc
        self.cached["donators"] = await self.update_donator_list()

    @cache_stats.before_loop
    async def task_waiter(self):
        await self.bot.wait_until_ready()

    @cache_stats.error
    async def cache_stats_error(self, error):
        logger.error(error)

    async def shutdown(self):
        await self.app.shutdown()
        await self.app.cleanup()

    async def run(self):
        await self.bot.wait_until_ready()
        if HOST is not None:
            try:
                logger.info(f"Starting webserver on {HOST}:{PORT}")
                await web._run_app(
                    self.app,
                    host=HOST,
                    port="6969",
                    access_log=logger,
                    print=None,
                    ssl_context=self.ssl_context,
                )
            except OSError as e:
                logger.warning(e)

    @staticmethod
    async def index(request):
        return web.Response(text="Welcome to Rival's IPC API!")

    async def update_donator_list(self):
        donators = []
        data = await self.bot.db.execute(
            """
            SELECT user_id FROM dnr
            """
        )
        for user_id in sorted(data, reverse=True):
            user=self.bot.get_user(int(user_id[0]))
            if user == None:
                pass
            else:    
                donators.append(
                {"name": user.name, "id":user.id}
                )
        return donators

    async def donator_list(self, request):
        return web.json_response(self.cached["donators"])

    # async def user_list(self, request):
    #     return web.json_response(str(self.bot.users))

    async def ping_handler(self, request):
        return web.Response(text=f"{self.bot.latency*1000}")

    async def website_statistics(self, request):
        return web.json_response(self.cached)

    async def command_list(self, request):
        return web.json_response(self.cached_command_list)

    def get_command_structure(self, command):
        if command.hidden or not command.enabled:
            return None

        subcommands = []
        if hasattr(command, "commands"):
            for subcommand in command.commands:
                subcommand_structure = self.get_command_structure(subcommand)
                if subcommand_structure:
                    subcommands.append(subcommand_structure)

        result = {
            "name": command.name,
            "usage": command.usage or command.signature,
            "description": command.short_doc,
            "subcommands": subcommands,
        }

        return result

    def generate_command_list(self):
        ignored_cogs = ["Jishaku", "Owner"]
        result = []
        for cog in self.bot.cogs.values():
            if cog.qualified_name in ignored_cogs:
                continue

            commands = cog.get_commands()
            if not commands:
                continue

            command_list = []
            for command in commands:
                command_structure = self.get_command_structure(command)
                if command_structure:
                    command_list.append(command_structure)

            if not command_list:
                continue

            cog_content = {
                "name": cog.qualified_name,
                "description": cog.description,
                "icon": getattr(cog, "icon", None),
                "commands": command_list,
            }

            result.append(cog_content)

        return result


async def setup(bot):
    await bot.add_cog(WebServer(bot))