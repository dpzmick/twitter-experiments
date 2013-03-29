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

if __name__ == "__main__":
    userID = pickUser()
    #db = setUpDB('66.228.60.19', 'new_tweets')
    #db = setUpDB('127.0.0.1', 'new_tweets')
    
    db_tweets    = setUpDB('141.142.226.111', 'tweets')
    db_followers = setUpDB('141.142.226.111', 'followers')

    tweets    = getCollection(db_tweets   , userID)
    followers = getCollection(db_followers, userID)
    
    findRetweets = findRetweetsQuicker

    print Fore.BLUE + "Getting users tweets" + Fore.RESET
    u_tweets = getUsersTweets(tweets, userID)
    print Fore.BLUE + "Found " + Fore.RED + str(len(u_tweets)) + Fore.RESET

    print Fore.BLUE + "Finding retweets" + Fore.RESET
    tweet_ids = []
    follower_amounts = []
    not_follower_amounts = []

    count = 1
    total = len(u_tweets)
    for tweet in u_tweets:
        print Fore.BLUE + 'id: ' + Fore.WHITE + str(tweet['id']) + ' ' + \
                str(count/float(total) * 100) + ' %' + Fore.RESET
        count += 1
        retweets = findRetweets(tweets, tweet)
        l = len(retweets)
        if not l == 0:
            tweet_ids.append(tweet['id'])

            print '\t' + Fore.BLUE + "Dividing retweets" + Fore.RESET
            retweets_slices = [retweets[x:x+100] for x in xrange(0, len(retweets), 100)]
            qs = [ 
                    {'$or' :
                        [ {"_id" : retweet['user']['id']} for retweet in retweets_slice]
                    }
                for retweets_slice in retweets_slices]

            f_count = reduce(lambda ac, q: ac + followers.find(q).count(), qs, 0)
            print '\tquery done'
            nf_count = l - f_count

            print '\t' + Fore.BLUE + 'l: ' + str(l) +' f: ' + str(f_count) + \
                    ' nf: ' + str(nf_count) + Fore.RESET

            follower_amounts.append(f_count)
            not_follower_amounts.append(nf_count)

            print "\tsleeping for a bit so mongo doesn't explode"
            time.sleep(5)

    # print "Average: " + str(sum(amounts)/len(amounts))
    numberOfRetweetsGraph(tweet_ids, follower_amounts, not_follower_amounts, userID)
