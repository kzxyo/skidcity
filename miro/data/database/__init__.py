from pymongo import MongoClient
import motor.motor_asyncio as mongodb


class Async(object):
    connection = mongodb.AsyncIOMotorClient("mongodb+srv://Claqz:lol12!@cluster0.9hvfo91.mongodb.net/")
    db = connection["ok"]["servers"]

class Sync(object):
    connection = mongodb.AsyncIOMotorClient("mongodb+srv://Claqz:lol12!@cluster0.9hvfo91.mongodb.net/")
    db = connection["ok"]["servers"]