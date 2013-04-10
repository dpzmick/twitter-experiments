# Get a single tweet by user out of database, find retweets, make a picture.

# local
from db import *
# not local
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
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

def pickTweet(tweets, userID):
    user_tweets = getUsersTweets(tweets, userID)
    print Fore.BLUE + "Options for Tweet to visualize:"
    for i, tweet in enumerate(user_tweets):
        print "%s%d: %s%s" % (Fore.RED, i, Fore.WHITE, tweet['text'])
    return user_tweets[int(raw_input(Fore.RED + "> " + Fore.RESET))]

# Pictures
# I am not proud of this..
def simpleBarChart(tweet, f_retweets, nf_retweets, interval, filename, saving):
    print Fore.BLUE + "Now making a nice picture" + Fore.RESET
    f_times = []
    for retweet in f_retweets:
        f_times.append(retweet['created_at'])

    nf_times = []
    for retweet in nf_retweets:
        nf_times.append(retweet['created_at'])

    times = f_times + nf_times
    # setup bins for bar graph.
    # range: time of first tweet -> time of last tweet
    first = min(times)
    last = max(times)

    f_intervals = {}
    nf_intervals = {}
    for time in f_times:
        elapsed_intervals = math.floor((time - first).total_seconds() / interval)
        f_intervals[elapsed_intervals] = f_intervals.get(elapsed_intervals, 0) + 1
        nf_intervals[elapsed_intervals] = nf_intervals.get(elapsed_intervals, 0)

    for time in nf_times:
        elapsed_intervals = math.floor((time - first).total_seconds() / interval)
        nf_intervals[elapsed_intervals] = nf_intervals.get(elapsed_intervals, 0) + 1
        f_intervals[elapsed_intervals] = f_intervals.get(elapsed_intervals, 0)

    #plt.yscale('symlog')
    plt.title(tweet['text'] + '\n' + tweet['user']['screen_name'])
    plt.ylabel('Retweets')
    plt.xlabel('%d second intervals after initial tweet (at %s)' \
            % (interval, str(tweet['created_at'])) )
    plt.bar(f_intervals.keys(), f_intervals.values(), color='r')
    plt.bar(nf_intervals.keys(), nf_intervals.values(), color='y',
            bottom=f_intervals.values())
    if saving:
        plt.savefig(filename)
        plt.close()
    else:
        plt.show()

# uhg, repeated code.
# TODO refactor
def non_interactive(use_relevance, interesting_tweet, retweets, userID, interval, filename):
    print Fore.BLUE + "Noninteractive retweet graph"
    db = setUpDB('141.142.226.111', 'tweets')
    tweets = getCollection(db, userID)
    
    db_followers = setUpDB('141.142.226.111', 'followers')
    followers = getCollection(db_followers, userID)

    relevance_interval = tweet_relevance(interesting_tweet, retweets)

    # Can't say I am proud of this either
    # Split up request into a couple of smaller ones.
    retweets_slices = [retweets[x:x+100] for x in xrange(0, len(retweets), 100)]
    qs = [
            {'$or' :
                [ {"_id" : retweet['user']['id']} for retweet in retweets_slice]
            }
        for retweets_slice in retweets_slices]

    relevant_followers = reduce(lambda ac, q: ac + \
            [el['_id'] for el in followers.find(q)], qs, [])

    f_retweets = []
    nf_retweets = []
    for retweet in retweets:
        et = (retweet['created_at'] - interesting_tweet['created_at']).total_seconds() 
        if not use_relevance or et <= relevance_interval:
            if retweet['user']['id'] in relevant_followers:
                f_retweets.append(retweet)
            else:
                nf_retweets.append(retweet)

    simpleBarChart(interesting_tweet, f_retweets, nf_retweets, interval, filename, True)

if __name__ == "__main__":
    use_relevance = True
    userID = pickUser()
    db = setUpDB('141.142.226.111', 'tweets')
    tweets = getCollection(db, userID)
    
    db_followers = setUpDB('141.142.226.111', 'followers')
    followers = getCollection(db_followers, userID)

    print Fore.BLUE + "Getting users tweets" + Fore.RESET
    _id = int(raw_input(Fore.RED + "Tweet Id >" + Fore.RESET))
    interesting_tweet = tweets.find_one({'id' : _id})
    print Fore.BLUE + "Using Tweet: " + Fore.WHITE + interesting_tweet['text']

    print Fore.BLUE + "Getting retweets (might take some time)" + Fore.RESET
    retweets = findRetweets(tweets, interesting_tweet)
    print Fore.BLUE + "Found %s%d%s" % (Fore.RED, len(retweets), Fore.RESET)

    relevance_interval = tweet_relevance(interesting_tweet, retweets)
    print Fore.BLUE + "Relevance interval: " + Fore.RED + str(relevance_interval) + Fore.RESET
    if not use_relevance:
        print Fore.BLUE + "But not using relevance" + Fore.RESET
    print Fore.BLUE + "Spliting into followers and non-followers" + Fore.RESET

    # Can't say I am proud of this either
    # Split up request into a couple of smaller ones.
    retweets_slices = [retweets[x:x+100] for x in xrange(0, len(retweets), 100)]
    qs = [
            {'$or' :
                [ {"_id" : retweet['user']['id']} for retweet in retweets_slice]
            }
        for retweets_slice in retweets_slices]

    relevant_followers = reduce(lambda ac, q: ac + \
            [el['_id'] for el in followers.find(q)], qs, [])

    f_retweets = []
    nf_retweets = []
    for retweet in retweets:
        et = (retweet['created_at'] - interesting_tweet['created_at']).total_seconds() 
        if not use_relevance or et <= relevance_interval:
            if retweet['user']['id'] in relevant_followers:
                f_retweets.append(retweet)
            else:
                nf_retweets.append(retweet)

    # lets loop it, make multiple pictures without reloading everything
    while True:
        # Will look at retweets per every <interval> seconds
        print Fore.BLUE + "Interval Size? (in seconds)" + Fore.RESET
        interval = int(raw_input(Fore.RED + "> " + Fore.RESET))
        print "%sUsing %s%d%s second intervals%s" % (Fore.BLUE, Fore.RED, interval,
            Fore.BLUE, Fore.RESET)
        simpleBarChart(interesting_tweet, f_retweets, nf_retweets, interval,
                None, False)
