# Get a single tweet by user out of database, find retweets, make a picture.

# local
from db import *
# not local
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import numpy as np
import math
import dateutil.parser
from colorama import init, Fore
init()
import time

# IO
def pickUser(id_list_name = '../id_list'):
    print Fore.BLUE + "Please pick a user to look at (ids loaded from %s)" % id_list_name
    ids = []
    id_list = open(id_list_name)
    for i, _id in enumerate(id_list):
        parts = _id.strip().split(':')
        ids.append(int(parts[1]))
        print "%s%d: %s%s" % (Fore.RED, i, Fore.WHITE, parts[0],)
    id_list.close()
    return ids[int(raw_input(Fore.RED + "> " + Fore.RESET))]

def numberOfRetweetsGraph(tweets, amounts, user_id):
    ind = np.arange(len(amounts))
    fig = plt.figure()
    ax = fig.add_subplot(111)
    rects = ax.bar(ind, amounts)

    ax.set_title('Retweets of ' + str(user_id) + '\'s tweets')
    ax.set_ylabel('Number of retweets')
    ax.set_xlabel('Tweet id')
    plt.show()

if __name__ == "__main__":
    userID = pickUser()
    #db = setUpDB('141.142.226.111', 'tweets')
    db = setUpDB('66.228.60.19', 'new_tweets')
    #db = setUpDB('127.0.0.1', 'new_tweets')
    tweets = getCollection(db, userID)
    findRetweets = findRetweetsQuicker

    print Fore.BLUE + "Getting users tweets" + Fore.RESET
    u_tweets = getUsersTweets(tweets, userID)
    print Fore.BLUE + "Found " + Fore.RED + str(len(u_tweets)) + Fore.RESET

    print Fore.BLUE + "Finding retweets" + Fore.RESET
    tweet_ids = []
    amounts = []
    for tweet in u_tweets:
        tweet_ids.append(tweet['id'])
        l = len(findRetweets(tweets, tweet))
        amounts.append(l)
        print str(tweet['id']) + ' ' + str(l)
    
    print "Average: " + str(sum(amounts)/len(amounts))
    numberOfRetweetsGraph(tweet_ids, amounts, userID)
