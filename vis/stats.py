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
import sys
import os

def all_user_ids(fname="../id_list"):
    users = {}
    users_f = open(fname)
    for line in users_f:
        parts = line.strip().split(':')
        users[parts[0]] = int(parts[1])
    return users

# display
def alert(string):
    print Fore.BLUE + string + Fore.RESET

def data(prompts, values):
    string = ""
    for prompt, value in zip(prompts, values):
        string += Fore.BLUE + prompt + ' ' + Fore.WHITE + str(value) + ' '
    print string + Fore.RESET

def get_data(_id, u_tweets, tweets, followers):
    # relevances: {id : relevance}
    relevances = {}
    # amounts: {id : [# rt by direct followers, # of rt non direct ] }
    amounts = {}

    count = 1
    total = len(u_tweets)
    for tweet in u_tweets:
        data(['id:', '%:'], [tweet['id'], count/float(total) * 100])

        retweets = findRetweets(tweets, tweet)

        l = len(retweets)
        f_count = how_many_direct_retweets(retweets, _id, followers)

        amounts[tweet['id']] = [f_count, l - f_count]
        if l == 0:
            relevances[tweet['id']] = 0
        else:
            relevances[tweet['id']] = tweet_relevance(tweet, retweets)
        count += 1

    return (relevances, amounts)


def rt_percent_computer(el):
    l = el[0] + el[1]
    if l == 0:
        return 0
    else:
        return float(el[0]) / l

def variance(lst, mean):
    squared_diffs = sum([(item - mean)**2 for item in lst])
    return squared_diffs / len(lst)

def var_graph(lst, title):
    ind = np.arange(len(lst))
    plt.bar(ind, lst)
    plt.title(title)
    plt.savefig(SESSION_NAME + '/' + title + '.pdf', bbox_inches=0)
    plt.close()

def var_stats(lst):
    avg = sum(lst)/len(lst)
    med = lst[int(math.floor(len(lst)/2))]
    mn = min(lst)
    mx = max(lst)
    stdev = math.sqrt(variance(lst, avg))
    return (avg, med, mn, mx, stdev)

def stats(_id, db_tweets, db_followers, screen_name):
    tweets    = getCollection(db_tweets   , _id)
    followers = getCollection(db_followers, _id)
    
    u_tweets = getUsersTweets(tweets, _id)
    data(["Found", "Tweets"], [len(u_tweets), ""])

    relevances, amounts = get_data(_id, u_tweets, tweets, followers)
    alert('Writing CSV')
    csv_f = open(SESSION_NAME + '/' + screen_name + '.csv', 'w')
    csv_f.write('ID, REL, DF_RT, IN_RT, TOT_RT, RT_PERCENT\n')
    for tweet in u_tweets:
        _id = tweet['id']
        csv_f.write('%d, %d, %d, %d, %d, %f' %
                (_id,
                relevances[_id],
                amounts[_id][0],
                amounts[_id][1],
                amounts[_id][0] + amounts[_id][1],
                rt_percent_computer(amounts[_id])))

        csv_f.write('\n')
    csv_f.close()


    alert("Doing stats")

    amts = map(lambda el: el[0] + el[1], amounts.values())
    # what percentage of rtweets were by direct followers
    rt_percents = map(rt_percent_computer, amounts.values())

    rel = sorted(relevances.values())
    amt = sorted(amts)
    per = sorted(rt_percents)

    # printing
    s = ""
    avg_amt, med_amt, min_amt, max_amt, amt_stdev = var_stats(amt)
    s += "Average Retweets: " + str(avg_amt) + "\n"
    s += "Median Retweets: " + str(med_amt) + "\n"
    s += "Min Retweets: " + str(min_amt) + "\n"
    s += "Max Rewtweets: " + str(max_amt) + "\n"
    s += "Retweet # stdev: " + str(amt_stdev) + "\n"
    var_graph(amt, screen_name + " Retweet Amounts")

    s += "\n"

    avg_rel, med_rel, min_rel, max_rel, rel_stdev = var_stats(rel)
    s += "Average Relevance: " + str(avg_rel) + "\n"
    s += "Median Relevance: " + str(med_rel) + "\n"
    s += "Min Relevance: " + str(min_rel) + "\n"
    s += "Max Relevance: " + str(max_rel) + "\n"
    s += "Relevance stdev: " + str(rel_stdev) + "\n"
    var_graph(rel, screen_name + " Relevance")

    s += "\n"

    avg_per, med_per, min_per, max_per, per_stdev = var_stats(per)
    s += "Average Follower RT percent: " + str(avg_per) + "\n"
    s += "Median Follower RT percent: " + str(med_per) + "\n"
    s += "Min Follower RT percent: " + str(min_per) + "\n"
    s += "Max Follower RT percent: " + str(max_per) + "\n"
    s += "Follower RT percent stdev: " + str(per_stdev) + "\n"
    var_graph(per, screen_name + " RT Percent")

    return s

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "usage: python stats.py <session-name>"
        sys.exit(2)
    
    SESSION_NAME = sys.argv[1]
    print "SESSION: " + SESSION_NAME
    if os.path.exists(SESSION_NAME):
        print "session already exists"
        sys.exit(2)

    os.makedirs(SESSION_NAME)

    db_tweets    = setUpDB('141.142.226.111', 'tweets')
    db_followers = setUpDB('141.142.226.111', 'followers')

    users = all_user_ids()

    stats_f = open(SESSION_NAME + '/stats.txt', 'w')
    for name in users:
        _id = users[name]
        data(["User:"], [name])
        s = stats(_id, db_tweets, db_followers, name)
        print s
        stats_f.write(name + "\n")
        stats_f.write("-----------------------------------------\n")
        stats_f.write(s)
        stats_f.write("\n")
        stats_f.flush()

    stats_f.close()
