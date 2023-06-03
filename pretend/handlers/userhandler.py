from  handlers.lastfmhandler import Handler
import json
from os.path import exists

users = {}

def read_db():
    if exists("users.json"):
        return json.loads(open("users.json").read())
    else:
        print("users db doesnt exist, creating new one")
        with open("users.json", "w") as outfile:
            json.dump(users, outfile)
            return read_db()

def update_db():
    with open("users.json", "w") as outfile:
            json.dump(users, outfile)

def get_user(id):
    if str(id) in users:
        return users[str(id)]
    else:
        return "error"

async def lastfm_user_exists(user):
    h = Handler("43693facbb24d1ac893a7d33846b15cc") 
    a = await h.get_user_info(user)
    return 'error' not in a

def link_user(id, user):
    users[str(id)] = user
    update_db()

def unlink_user(id, user):
    users
    update_db()