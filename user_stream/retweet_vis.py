# Get a single tweet by user out of database, find retweets, make a picture.

import matplotlib.pyplot as plt
import pymongo
import math
import dateutil.parser
import difflib

userid = 428333
conn = pymongo.Connection('66.228.60.19')
db = conn['tweets']
tweets = db[str(userid)]

# TODO need a better way of looking at specific tweets.
possible_tweets = []
count = 0
print "Options:"
for tweet in tweets.find({'user.id' : userid}):
    print str(count) + ": " + tweet['text']
    count += 1
    possible_tweets.append(tweet)

print 
print "Please Select a tweet to look at:"
selection = int(raw_input(">"))
origin_tweet = possible_tweets[selection]

print "Using Tweet: " + origin_tweet['text']

# find retweets
# note: retweet count in stored tweet is not accurate
# tweet was stored before any retweets could have been made
# TODO evaluate if there is a better way to do this.
print "Getting retweets"

retweets = []
# misses some
for tweet in tweets.find({'retweeted_status.text' : origin_tweet['text']}):
    retweets.append(tweet)

# slow, and still doesn't report same amount as twitter's website.
#for tweet in tweets.find():
#    if difflib.SequenceMatcher(None, tweet['text'],
#            origin_tweet['text']).ratio() > 0.6:
#        retweets.append(tweet)

print "Found %d" % len(retweets)

print "Now making a nice picture"
times = []
for retweet in retweets:
    times.append(dateutil.parser.parse(retweet['created_at']))

# setup bins for bar graph.
# range: time of first tweet -> time of last tweet
first = min(times)
last = max(times)

# Will look at retweets per every <interval> seconds
print "Interval Size? (in seconds)"
interval = int(raw_input(">"))
print "Using %d second intervals" % interval

intervals = {}
for time in times:
    elapsed_intervals = math.floor((time - first).total_seconds() / interval)
    intervals[elapsed_intervals] = intervals.get(elapsed_intervals, 0) + 1

plt.bar(intervals.keys(), intervals.values())
plt.show()
