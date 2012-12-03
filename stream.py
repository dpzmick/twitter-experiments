import getpass
import pycurl
import json
import threading
import pymongo
from pymongo import Connection
import urllib

# I connect to the streaming api and fetch tweets. I call a callback when the
# tweets are fetched.
class Client:
    # track - comma separated list of keywords to track
    # locations - set of bounding boxes to track.
    def __init__(self, url, callback, username, passwd, track="", locations=""):
        self.buff = ""
        self.conn = pycurl.Curl()
        self.url = url
        
        post_dict = {}
        if track != '':
            post_dict["track"] = track
        if locations != '':
            post_dict["locations"] = locations
        self.post = urllib.urlencode(post_dict)

        self.callback = callback
        self.username = username
        self.passwd = passwd
        #threading.Thread.__init__(self)
        

    def run(self):
        self.conn.setopt(pycurl.POST, 1)
        self.conn.setopt(pycurl.POSTFIELDS, self.post)
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
    # only print a tweet if it doesn't have text (isn't actually a tweet)
    if tweet.get('text', -1) == -1:
        print tweet

def store_in_mongo(tweet):
    try:
        db.raw.insert(tweet)
        print_tweet(tweet)
    except:
        print ""
        print "FAILED TO STORE A TWEET"
        print ""
        return


STREAM_URL = "https://stream.twitter.com/1/statuses/filter.json"
USER = "dpzmick"
PASS = getpass.getpass()

mongoConn = Connection()
db = mongoConn.tweets

# gets any geotagged tweet
c = Client(STREAM_URL, store_in_mongo, USER, PASS, '', '-180,-90,180,90') 
c.run()
