# generates a CSV file to feed into OpenHeatMap
# negative = -1
# positive = +1

# each row gets lat, long, value
rows = []

from pymongo import Connection
conn = Connection()
db = conn.tweets
collection = db.flu_classified

for tweet in collection.find():
    if tweet['geo'] != None:
        rows.append( (tweet['geo']['coordinates'][0],
            tweet['geo']['coordinates'][1], tweet['sentiment'],
            tweet['cleanedText']) )


delimit = ','
f = open('out.csv', 'w')
f.write('latitude' + delimit + 'longitude' + delimit + 'value' + delimit + 'content\n')
for row in rows:
    string = '%s%s %s%s %s\n' % (row[0], delimit, row[1], delimit, row[2])
    f.write(string)
f.close()
