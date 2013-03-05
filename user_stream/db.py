# a couple of handy functions for accessing the database
import pymongo
import difflib

def setUpDB(addr='66.228.60.19', _db='tweets'):
    conn = pymongo.Connection(addr)
    db = conn[_db]
    return db

def getCollection(db, userID):
    return db[str(userID)]

def getUsersTweets(tweets, userID):
    user_tweets = []
    for tweet in tweets.find({'user.id' : userID}):
        user_tweets.append(tweet)
    return user_tweets

def findRetweetsQuicker(tweets, i_tweet):
    retweets = []
    for tweet in tweets.find({'retweeted_status.text' : i_tweet['text']}):
        retweets.append(tweet)
    return retweets

def findRetweetsSlower(tweets, i_tweet):
    retweets = []
    for tweet in tweets.find():
        if difflib.SequenceMatcher(None, tweet['text'], i_tweet['text']).ratio() > 0.6:
            retweets.append(tweet)
    return retweets
