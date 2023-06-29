import sys


sys.path.append("../")

import asyncio
import json
import os

from discord.ext.ipc import Client
from quart import Quart, jsonify, redirect, render_template, request

from helpers.wock import Database, Redis


config = json.loads(open("../config.json", "r").read())

app = Quart(__name__, subdomain_matching=True, static_url_path="", static_folder="static")
app.config["SERVER_NAME"] = config.get("domain")


_IPC = Client(
    host="0.0.0.0",
    secret_key="M8XV07GPjmMKA",
    standard_port=3218,
    do_multicast=False,
)
database = Database(config)
redis = Redis


@app.errorhandler(Exception)
async def error_handler(error):
    print(error)
    status = error.args[1] if len(error.args) > 1 else 400
    return (
        jsonify(
            {
                "error": f"{status}: Bad Request",
                "message": (error.args[0] if len(error.args) > 0 else "An unknown error occurred."),
            }
        ),
        status,
    )


@app.errorhandler(404)
async def not_found(error):
    return (
        jsonify(
            {
                "error": "404: Not Found",
                "message": "The requested resource could not be found.",
            }
        ),
        404,
    )


@app.errorhandler(405)
async def invalid_method(error):
    return (
        jsonify(
            {
                "error": "405: Invalid method",
                "message": f"The requested resource doesn't support the {request.method} method.",
            }
        ),
        405,
    )


@app.errorhandler(500)
async def internal_server_error(error):
    return (
        jsonify(
            {
                "error": "500: Internal Server Error",
                "message": "An internal server error occurred.",
            }
        ),
        500,
    )


@app.route("/")
async def index():
    return redirect("https://discord.gg/wock")


@app.route("/commands")
@app.route("/cmds")
@app.route("/help")
async def commands():
    data = await _IPC.request("commands")

    return await render_template("commands.html", bot=data["bot"], commands=data["commands"])


@app.route("/discord")
@app.route("/support")
async def discord():
    return redirect("https://discord.gg/wock")


@app.route("/invite")
async def invite():
    return redirect("https://discordapp.com/oauth2/authorize?client_id=1004859044974039211&scope=bot+applications.commands&permissions=8")


@app.route("/avatars/<int:user_id>")
async def avatars(user_id):
    # return redirect(f"https://beta.wock.cloud/avatars/{user_id}")
    data = await _IPC.request("avatars", user_id=user_id)
    if error := data.get("error"):
        raise ValueError(error)

    return await render_template(
        "avatars.html",
        data=data,
    )


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    asyncio.set_event_loop(loop)

    loop.run_until_complete(database.connect())
    redis = loop.run_until_complete(redis.from_url())
    for route in os.listdir("routes"):
        if route.endswith(".py"):
            router = __import__(f"routes.{route[:-3]}", fromlist=["*"]).router
            router.ipc = _IPC
            router.database = database
            router.redis = redis
            router.config = config
            router.app = app
            app.register_blueprint(router)
    try:
        app.run(host="0.0.0.0", port=3217, debug=False, loop=loop)
    except KeyboardInterrupt:
        print("Shutting down...")
        loop.close()
