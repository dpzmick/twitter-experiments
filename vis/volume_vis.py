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

def numberOfRetweetsGraph(tweets, follower_amounts, not_follower_amounts, user_id):
    ind = np.arange(len(follower_amounts))
    fig = plt.figure()
    ax = fig.add_subplot(111)
    rects1 = ax.bar(ind, follower_amounts, color='r')
    rects2 = ax.bar(ind, not_follower_amounts, color='y',
            bottom=follower_amounts)
    
    ax.set_title('Retweets of ' + str(user_id) + '\'s tweets')
    ax.set_ylabel('Number of retweets')
    ax.set_xlabel('Tweet id')
    plt.show()

# display
def alert(string):
    print Fore.BLUE + string + Fore.RESET

def data(prompts, values):
    string = ""
    for prompt, value in zip(prompts, values):
        string += Fore.BLUE + prompt + ' ' + Fore.WHITE + str(value) + ' '
    print string + Fore.RESET

if __name__ == "__main__":
    userID = pickUser()
    db_tweets    = setUpDB('141.142.226.111', 'tweets')
    db_followers = setUpDB('141.142.226.111', 'followers')

    tweets    = getCollection(db_tweets   , userID)
    followers = getCollection(db_followers, userID)
    
    alert("Getting users tweets")
    u_tweets = getUsersTweets(tweets, userID)
    data(["Found"], [len(u_tweets)])

    alert("Finding retweets for each user tweet")
    tweet_ids = []

    follower_amounts = []
    not_follower_amounts = []

    count = 1
    total = len(u_tweets)

    for tweet in u_tweets:
        data(['id:', '%'], [tweet['id'], count/float(total) * 100])

        retweets = findRetweets(tweets, tweet)
        l = len(retweets)
        if not l == 0:
            tweet_ids.append(tweet['id'])
            f_count = how_many_direct_retweets(retweets, userID, followers)
            nf_count = l - f_count
            follower_amounts.append(f_count)
            not_follower_amounts.append(nf_count)
            data(['  l:', 'f:', 'nf:'], [l, f_count, nf_count])

        count += 1
    amounts = follower_amounts + not_follower_amounts
    print "Average: " + str(sum(amounts)/len(amounts))
    numberOfRetweetsGraph(tweet_ids, follower_amounts, not_follower_amounts, userID)
