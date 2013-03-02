# Prints a time series following a specific tweet, assuming only the original
# tweet and retweets in collection (for now)

# this version assumes that a collection in mongo contains all retweets of a
# tweet.

# it does not attempt to do any sort of filtering, it simply grabs all of the
# tweets in the collection and plots them.

# the plot compares shows volume of tweets in some time period.

import numpy as np
import matplotlib.pyplot as plt
import pymongo
import math
import dateutil.parser

userid = 428333
conn = pymongo.Connection('66.228.60.19')
db = conn['followed_tweets']
tweets = db[str(userid)]

# get times out of database
times = []
for tweet in tweets.find():
    # Time stored in tweet is in UTC (from twitter API)
    times.append(dateutil.parser.parse(tweet['created_at']))

# setup bins for bar graph.
# range: time of first tweet -> time of last tweet
first = min(times)
last = max(times)

# Will look at retweets per every <interval> seconds
interval = 3600 * 24

intervals = {}
for time in times:
    elapsed_intervals = math.floor((time - first).total_seconds() / interval)
    intervals[elapsed_intervals] = intervals.get(elapsed_intervals, 0) + 1

plt.bar(intervals.keys(), intervals.values())
plt.show()
