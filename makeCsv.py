# generates a CSV file to feed into OpenHeatMap
# negative = -1
# positive = +1

# for ease, Country Code -> (Running Total, number of tweets)
# average can be computed later
countrySentiment = {}

from pymongo import Connection
conn = Connection()
db = conn.tweets
collection = db.classified

for tweet in collection.find():
    val = 0
    if tweet['sentiment'] == 'neg':
        val = -1
    elif tweet['sentiment'] == 'pos':
        val = 1
    
    if tweet['place'] == None:
        #TODO find country of non-tagged tweets using geo data
        pass
        #print 'No place!'
    else:
        #print tweet['_id']
        countryCode = tweet['place']['country']
        runningTotal = countrySentiment.get(countryCode, (0,0))[0] + val
        numberOfTweets = countrySentiment.get(countryCode, (0,0))[1] + 1.0
        countrySentiment[countryCode] = (runningTotal, numberOfTweets)

print countrySentiment

# do the averages.

for key in countrySentiment.keys():
    tup = countrySentiment[key]
    countrySentiment[key] = tup[0] / tup[1]

print countrySentiment

delimit = '\t'
f = open('out.csv', 'w')
f.write('country_name' + delimit + 'value\n')
for key in countrySentiment.keys():
    string = '%s%s%s\n' % (key, delimit, countrySentiment[key])
    f.write(string)
f.close()
