import json
from os.path import exists
from cogs.utils import fmhandler
users = {}

def read_db():
    if exists("users.json"):
        return json.loads(open("users.json").read())
    else:
        print("users db doesnt exist, creating new one")
        with open("users.json", "w") as outfile:
            json.dump(users, outfile)
            return read_db()

def updatedb():
    with open("users.json", "w") as outfile:
            json.dump(users, outfile)

def getuser(id):
    if str(id) in users:
        return users[str(id)]
    else:
        return "error"

async def userexists(user):
    a = await fmhandler.getui(user)
    return 'error' not in a

def linkuser(id, user):
    users[str(id)] = user
    updatedb()

def unlinkuser(id, user):
    users
    updatedb()