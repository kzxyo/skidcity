import json
from os.path import exists

config_placeholder = {
    "apikey": "lastfm api key here"
    #i dont fucking know why i did this shit
}

config = {}


def readconfig() -> dict:
    if exists("config.json"):
        return json.loads(open("config.json").read())
    else:
        print("couldnt find config file, creating new one")
        with open("config.json", "w") as outfile:
            json.dump(config_placeholder, outfile)
        return readconfig()


def get_config():
    global config
    if not config:
        config = readconfig()
    return config