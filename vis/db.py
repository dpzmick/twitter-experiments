# a couple of handy functions for accessing the database
import pymongo
import difflib
import re

def setUpDB(addr='66.228.60.19', _db='tweets'):
    conn = pymongo.Connection(addr)
    db = conn[_db]
    return db

def getCollection(db, userID):
    return db[str(userID)]

def getUsersTweets(tweets, userID):
    q = {'user.id' : userID}
    return [tweet for 
            tweet in tweets.find(q).sort('created_at', 1).batch_size(100000)]

# add date option to both
def findRetweetsQuicker(tweets, i_tweet):
    q = {"$and" : 
            [
                { "user.id" : { "$ne" : i_tweet["user"]["id"] } }, 
                { "retweeted_status.text" : i_tweet['text'] },
                { "created_at" : { "$gte" : i_tweet['created_at'] } }
            ]
        }
    return [tweet for tweet in tweets.find(q).batch_size(100000)]

def findRetweetsSlower(tweets, i_tweet):
    r = re.compile(".*" + i_tweet['text'] + "*", re.IGNORECASE)
    q = {'$and' :
            [
                { 'user.id' : { "$ne" : i_tweet["user"]["id"] } },
                { 'text' : {'$regex' : r } },
                { "created_at" : { "$gte" : i_tweet['created_at'] } }
            ]
        }
    return [tweet for tweet in tweets.find(q).batch_size(100000)]
