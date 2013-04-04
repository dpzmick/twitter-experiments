# a couple of handy functions for accessing the database
import pymongo
import difflib
import re
import math

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

# ANALYSIS
# If retweet amount drops below amount_c for interval_c intervals of time_c
# seconds, the tweet is considered to no longer be "relevant"
# Returns number of seconds tweet remains relevant (rounded to the nearest
# interval size)
# If tweet never becomes irrrelevant, returns seconds between first tweet and
# last retweet
def tweet_relevance(tweet, retweets, time_c=3600, amount_c=10, interval_c=5):
    first = tweet['created_at']
    last = None
    intervals = {}
    for tweet in retweets:
        time = tweet['created_at']
        if last == None or time > last:
            last = time
        elapsed_intervals = int(math.floor((time - first).total_seconds() / time_c))
        intervals[elapsed_intervals] = intervals.get(elapsed_intervals, 0) + 1
    
    below_threshold_count = 0
    last_interval = 0
    for i in range(0,sorted(intervals.keys())[-1]):
        count = intervals.get(i,0)
        if count >= amount_c:
            below_threshold_count = 0
        if count < amount_c:
            below_threshold_count += 1
        if below_threshold_count == interval_c:
            return (i - interval_c + 1) * time_c
    return (last - first).total_seconds()

