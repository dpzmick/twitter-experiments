import getpass
import pycurl
import json
import threading
import pymongo
from pymongo import Connection

# I connect to the streaming api and fetch tweets. I call a callback when the
# tweets are fetched.
class Client(threading.Thread):
    # words should be in format "track=#Texas"
    def __init__(self, url, words, callback, username, passwd):
        self.buff = ""
        self.conn = pycurl.Curl()
        self.url = url
        self.words = words
        self.callback = callback
        self.username = username
        self.passwd = passwd
        threading.Thread.__init__(self)
        

    def run(self):
        self.conn.setopt(pycurl.POST, 1)
        self.conn.setopt(pycurl.POSTFIELDS, self.words)
        self.conn.setopt(pycurl.HTTPHEADER, ["Connection: keep-alive", "Keep-Alive: 3000"])
        self.conn.setopt(pycurl.USERPWD, "%s:%s" % (self.username, self.passwd))
        self.conn.setopt(pycurl.URL, self.url)
        self.conn.setopt(pycurl.WRITEFUNCTION, self.on_tweet)
        self.conn.perform()

    def on_tweet(self, data):
        self.buff += data
        if (data.endswith("\r\n") and self.buff.strip()):
            # buffer contains one full tweet. Parse it and send it to callback.
            tweet = json.loads(self.buff)
            self.buff = ""
            self.callback(tweet)

def print_tweet(tweet):
    print tweet['text']

def store_in_mongo(tweet):
    try:
        db.unclassified.insert(tweet)
        print_tweet(tweet)
    except:
        print ""
        print "FAILED TO STORE A TWEET"
        print ""
        return


STREAM_URL = "https://stream.twitter.com/1/statuses/filter.json"
WORDS = "track=yolo"
USER = "dpzmick"
PASS = getpass.getpass()

mongoConn = Connection()
db = mongoConn.tweets

c = Client(STREAM_URL, WORDS, store_in_mongo, USER, PASS)
c.start()
