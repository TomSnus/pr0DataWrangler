
import requests
import datetime
import time
from pymongo import MongoClient


def loadPosts(url):
    resp = requests.get(url)
    responseData = resp.json()
    return responseData['items']


def insertPosts(db, arr, maxid):
    if (maxid == -1):
        db.posts.insert_many(arr)
        print('Inserted initial dump!')
    else:
        newArr = []
        for i in range(0, len(arr)):
            if (arr[i]['id'] > maxid):
                newArr.append(arr[i])
        if (len(newArr) > 0):
            db.posts.insert_many(newArr)
            print('Inserted ' + str(len(newArr)) + ' items!')
        else:
            print('Nothing to insert!')


def readPosts(db, arr):

    res = db.posts.find_one(sort=[("id", -1)])
    if (res == None):

        insertPosts(db, arr, -1)
    else:
        insertPosts(db, arr, res['id'])


def readPostComment(db, id, arr):
    if (len(arr) > 0):
        for i in range(0, len(arr)):
            res = db.comments.find_one({"id": arr[i]['id']})
            if (res == None):
                arr[i]['theadid'] = id
                arr[i].pop('mark', None)
                arr[i].pop('confidence', None)
                arr[i].pop('parent', None)
                db.comments.insert(arr[i])


def readPostTag(db, id, arr):
    if (len(arr) > 0):
        for i in range(0, len(arr)):
            res = db.tags.find_one({"id": arr[i]['id']})
            if (res == None):
                arr[i]['theadid'] = id
                db.tags.insert(arr[i])


def loadPostInfo(db, id):
    resp = requests.get('http://pr0gramm.com/api/items/info?itemId=' + str(id))
    responseData = resp.json()
    readPostComment(db, id, responseData['comments'])
    readPostTag(db, id, responseData['tags'])

def readPostInfo(db):

    twoDaysAgo = datetime.datetime.now() - datetime.timedelta(hours=2)
    tmTwoDaysAgo = round(twoDaysAgo.timestamp())
    res = db.posts.find({"created": {"$gt": tmTwoDaysAgo}})
    for post in res:
        loadPostInfo(db, post['id'])

def readLastestPostInfo(db, arr):
    for i in range(0, len(arr)):
        loadPostInfo(db, arr[i]['id'])

def main():

    client = MongoClient('mongodb://localhost:27017')
    db = client.test


    readPostInfo(db)

    while 1 == 1:
        res = db.posts.find_one(sort=[("id", -1)])
        if (res == None):
            print("Starting new instance")
            resultPosts = loadPosts("http://pr0gramm.com/api/items/get?flags=15")
        else:
            print("Pos: " + str(res['id']))
            resultPosts = loadPosts("http://pr0gramm.com/api/items/get?id=" + str(res['id']) + "&flags=15")
        readPosts(db, resultPosts)
        readLastestPostInfo(db, resultPosts)

main()