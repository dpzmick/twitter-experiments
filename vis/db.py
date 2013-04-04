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

# queries
# takes a list of retweets and returns the number of them that were made by
# direct followers
def how_many_direct_retweets(retweets, user_id, followers):
    retweets_slices = [retweets[x:x+100] for x in xrange(0, len(retweets), 100)]
    qs = [{'$or' : 
            [{"_id" : retweet['user']['id']} for retweet in retweets_slice]} 
        for retweets_slice in retweets_slices]
    return reduce(lambda ac, q: ac + followers.find(q).count(), qs, 0)

def findRetweets(tweets, i_tweet):
    q = {"$and" : 
            [
                { "created_at" : { "$gte" : i_tweet['created_at'] } },
                { "retweeted_status.user.id" : i_tweet['user']['id']},
                { "retweeted_status.text" : i_tweet['text'] }
            ]
        }
    p = {'user.id' : 1, 'created_at' : 1}
    return [tweet for tweet in tweets.find(q, p).batch_size(100000)]
