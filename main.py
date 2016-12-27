from dbot.bot import Bot
from pymongo import MongoClient

mongo = MongoClient()
db = mongo["ene"]

x = Bot("<your token here>", db)

x.enable_extension("util")
x.enable_extension("help")

x.start()
