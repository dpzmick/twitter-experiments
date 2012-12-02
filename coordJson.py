# dumps latest how many tweets to JSON.
howMany = 2000

print 'Loading Data'
from pymongo import Connection
conn = Connection()
db = conn.tweets
collection = db.classified

data = {}
for tweet in collection.find().sort([("created_at", 1)]).limit(howMany):
    _id = str(tweet["_id"])

    value = 0
    if tweet['sentiment'] == 'neg':
        value = -1
    elif tweet['sentiment'] == 'pos':
        value = 1

    if tweet['geo'] != None:
        coords = [tweet['geo']['coordinates'][0], tweet['geo']['coordinates'][1]]
        data[_id] = {"value" : value, "center" : coords}

# print data

print 'Writing File'
import json
f = open("out.json", 'w')
f.write(json.dumps(data))
f.close()
