from pymongo import MongoClient
import pprint

client = MongoClient("mongodb://localhost:27017")

db = client.test

def find():
    tags = db.tags.find({"tag" : "nsfp"})
    for a in tags:
        pprint.pprint(a)

find()