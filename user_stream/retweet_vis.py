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
def simpleBarChart(tweet, retweets):
    print Fore.BLUE + "Now making a nice picture" + Fore.RESET
    times = []
    for retweet in retweets:
        times.append(dateutil.parser.parse(retweet['created_at']))

    # setup bins for bar graph.
    # range: time of first tweet -> time of last tweet
    first = min(times)
    last = max(times)
    print Fore.BLUE + "First: " + Fore.RED + str(first) + Fore.RESET
    print Fore.BLUE + "Last: " + Fore.RED + str(last) + Fore.RESET

    # Will look at retweets per every <interval> seconds
    print Fore.BLUE + "Interval Size? (in seconds)" + Fore.RESET
    interval = int(raw_input(Fore.RED + "> " + Fore.RESET))
    print "%sUsing %s%d%s second intervals%s" % (Fore.BLUE, Fore.RED, interval,
            Fore.BLUE, Fore.RESET)

    intervals = {}
    for time in times:
        elapsed_intervals = math.floor((time - first).total_seconds() / interval)
        intervals[elapsed_intervals] = intervals.get(elapsed_intervals, 0) + 1

    plt.title(tweet['text'] + '\n' + tweet['user']['screen_name'])
    plt.ylabel('Retweets')
    plt.xlabel('%d second intervals after initial tweet' % interval)
    plt.bar(intervals.keys(), intervals.values())
    plt.show()

if __name__ == "__main__":
    userID = pickUser()
    db = setUpDB()
    tweets = getCollection(db, userID)

    print Fore.BLUE + "Getting users tweets" + Fore.RESET
    interesting_tweet = pickTweet(tweets, userID)
    print Fore.BLUE + "Using Tweet: " + Fore.WHITE + interesting_tweet['text']

    print Fore.BLUE + "Getting retweets (might take some time)" + Fore.RESET
    retweets = findRetweetsQuicker(tweets, interesting_tweet)
    print Fore.BLUE + "Found %s%d%s" % (Fore.RED, len(retweets), Fore.RESET)
    
    simpleBarChart(interesting_tweet, retweets)
