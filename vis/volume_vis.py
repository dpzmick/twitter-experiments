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
    count = 1
    total = len(u_tweets)

    all_tweets = {}
    amounts = []
    relevances = {}
    for tweet in u_tweets:
        data(['id:', '%:'], [tweet['id'], count/float(total) * 100])

        retweets = findRetweets(tweets, tweet)
        l = len(retweets)
        if not l == 0:
            amounts.append(l)
            all_tweets[tweet['id']] = retweets
            relevances[tweet['id']] = tweet_relevance(tweet, retweets)
            print relevances[tweet['id']]
        count += 1
         
    rel = sorted(relevances.values())
    amt = sorted(amounts)

    avg_amt = sum(amt)/len(amt)
    med_amt = amt[int(math.floor(len(amt)/2))]
    avg_rel = sum(rel)/len(rel)
    med_rel = rel[int(math.floor(len(rel)/2))]
    print "Average Retweets: " + str(avg_amt)
    print "Median Retweets: " + str(med_amt)
    print "Average Relevance: " + str(avg_rel)
    print "Median Relevance: " + str(med_rel)

    alert("Pruning uninteresting tweets")
    tweet_ids = []
    follower_amounts = []
    not_follower_amounts = []
    count = 0
    for tweet_id, retweets in all_tweets.iteritems():
        l = len(retweets)
        r = relevances[tweet_id]
        if l >= avg_amt or r >= avg_rel:
            # TODO find more pythonic way to do this
            flags = []
            if l >= avg_amt:
                flags += ['amt']
            if r >= avg_rel:
                flags += ['rel'] 

            tweet_ids.append(tweet_id)
            f_count = how_many_direct_retweets(retweets, userID, followers)
            nf_count = l - f_count
            follower_amounts.append(f_count)
            not_follower_amounts.append(nf_count)
            percentage = count/float(total) * 100
            data(['id:','l:', 'f:', 'nf:', 'r'],
                    [tweet_id, l, f_count, nf_count, r])
            print "\t" + str(flags)
        count += 1


    numberOfRetweetsGraph(tweet_ids, follower_amounts, not_follower_amounts, userID)
