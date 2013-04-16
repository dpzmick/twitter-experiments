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
import retweet_vis as rtvis
import twitter
import hashlib

def all_user_ids(fname="../id_list"):
    users = {}
    users_f = open(fname)
    for line in users_f:
        parts = line.strip().split(':')
        users[parts[0]] = int(parts[1])
    return users

def write_tweets_csv(screen_name, u_tweets, amounts, relevances, info):
    alert('Writing CSV')
    csv_f = open(SESSION_NAME + '/' + screen_name + '.csv', 'w')
    csv_f.write('ID, ID_HASH, REL, DF_RT, IN_RT, TOT_RT, RT_PERCENT\n')
    for tweet in u_tweets:
        _id = tweet['id']
        if CSV_INTRUIGE:
            tot = amounts[_id][0] + amounts[_id][1]
            per = rt_percent_computer(amounts[_id])
            if relevances[_id] < info[1] and tot < info[0]:# and per > info[1]:
                continue
        csv_f.write('"%d", %s, %d, %d, %d, %d, %f' %
                (_id,
                hashlib.sha1(str(_id).encode("UTF-8")).hexdigest()[:6],
                relevances[_id],
                amounts[_id][0],
                amounts[_id][1],
                amounts[_id][0] + amounts[_id][1],
                rt_percent_computer(amounts[_id])))

        csv_f.write('\n')
    csv_f.close()

# display
def alert(string):
    print Fore.BLUE + string + Fore.RESET

def data(prompts, values):
    string = ""
    for prompt, value in zip(prompts, values):
        string += Fore.BLUE + prompt + ' ' + Fore.WHITE + str(value) + ' '
    print string + Fore.RESET

def get_data(_id, u_tweets, tweets, followers, screen_name):
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

        if RETWEET_VIS and len(retweets) > 0 and relevances[tweet['id']] > 0:
            dirname = SESSION_NAME + '/' + screen_name
            filename = dirname + '/' + str(tweet['id']) + '.pdf' 
            if not os.path.exists(dirname):
                os.makedirs(SESSION_NAME + '/' + screen_name)
            rtvis.non_interactive(True, tweet, retweets, _id, 1800, filename)
    return (relevances, amounts)


def rt_percent_computer(el):
    l = el[0] + el[1]
    if l == 0:
        return 0
    else:
        return float(el[0]) / l

def var_graph(lst, title):
    plt.hist(lst)
    plt.title(title)
    plt.savefig(SESSION_NAME + '/' + title + '.pdf', bbox_inches=0)
    plt.close()

def var_stats(lst):
    avg = sum(lst)/len(lst)
    med = lst[int(math.floor(len(lst)/2))]
    mn = min(lst)
    mx = max(lst)
    return (avg, med, mn, mx)

def stats(_id, db_tweets, db_followers, screen_name):
    tweets    = getCollection(db_tweets   , _id)
    followers = getCollection(db_followers, _id)
    
    u_tweets = getUsersTweets(tweets, _id)
    data(["Found", "Tweets"], [len(u_tweets), ""])

    tot_tweets = len(u_tweets)
    followers_count = API.GetUser(_id).GetFollowersCount()
    relevances, amounts = get_data(_id, u_tweets, tweets, followers, screen_name)

    alert("Doing stats")
    amts = map(lambda el: el[0] + el[1], amounts.values())
    # what percentage of rtweets were by direct followers
    rt_percents = map(rt_percent_computer, amounts.values())

    rel = [rele for rele in sorted(relevances.values()) if rele != 0]
    amt = sorted(amts)
    per = [perc for perc in sorted(rt_percents) if perc != 0]

    # printing
    avg_amt, med_amt, min_amt, max_amt = var_stats(amt)
    print "Average Retweets: " + str(avg_amt)
    print "Median Retweets: " + str(med_amt)
    print "Min Retweets: " + str(min_amt)
    print "Max Rewtweets: " + str(max_amt)
    print

    avg_rel, med_rel, min_rel, max_rel = var_stats(rel)
    print "Average Relevance: " + str(avg_rel)
    print "Median Relevance: " + str(med_rel)
    print "Min Relevance: " + str(min_rel)
    print "Max Relevance: " + str(max_rel)
    print

    avg_per, med_per, min_per, max_per = var_stats(per)
    print "Average Follower RT percent: " + str(avg_per)
    print "Median Follower RT percent: " + str(med_per)
    print "Min Follower RT percent: " + str(min_per)
    print "Max Follower RT percent: " + str(max_per)

    if VAR_GRAPH:
        var_graph(amt, screen_name + " Retweet Amounts")
        var_graph(rel, screen_name + " Relevance")
        var_graph(per, screen_name + " RT Percent")
    
    csv_info = (med_amt, med_rel, med_per)
    write_tweets_csv(screen_name, u_tweets, amounts, relevances, csv_info)
    s = "%s,%d,%d,%d,%f,%d\n" % (screen_name, followers_count, avg_amt, avg_rel,
            avg_per, tot_tweets)
    return s

if __name__ == "__main__":
    # FEATURES
    VAR_GRAPH = False
    RETWEET_VIS = False
    CSV_INTRUIGE = True

    if len(sys.argv) < 2:
        print "usage: python stats.py <session-name>"
        sys.exit(2)
    
    SESSION_NAME = sys.argv[1]
    print "SESSION: " + SESSION_NAME
    if os.path.exists(SESSION_NAME):
        print "session already exists"
        sys.exit(2)

    os.makedirs(SESSION_NAME)

    API = twitter.Api(consumer_key='8xZFzgdHPQDhceJWLXmH3g',
                      consumer_secret='NvEG1Kh54R8VE0bsIV6sw2u35iFcuYXaciUdxlbzQc',
                      access_token_key='14080233-7fxHD0cRyrAP9ZsglSoj1Saq9xPh6xI1pq984viOm',
                      access_token_secret='hlc1k5rtvrVtUBCnB9tHBp4whSGOpfagY9XE7X6FxA')

    db_tweets    = setUpDB('141.142.226.111', 'tweets')
    db_followers = setUpDB('141.142.226.111', 'followers')

    users = all_user_ids()

    stats_f = open(SESSION_NAME + '/stats.csv', 'w')
    stats_f.write('name,followers,amt,rel,direct_percent,total_tweets\n')
    for name in users:
        _id = users[name]
        data(["User:"], [name])
        s = stats(_id, db_tweets, db_followers, name)
        stats_f.write(s)
        stats_f.flush()

    stats_f.close()
