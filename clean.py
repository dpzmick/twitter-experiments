# a VERY VERY primitive twitter data cleaning script.

from pymongo import Connection
from nltk.corpus import stopwords
import nltk
 
# http://www.algorithm.co.il/blogs/programming/python/cheap-language-detection-nltk/
ENGLISH_STOPWORDS = set(nltk.corpus.stopwords.words('english'))
NON_ENGLISH_STOPWORDS = set(nltk.corpus.stopwords.words()) - ENGLISH_STOPWORDS
 
STOPWORDS_DICT = {lang: set(nltk.corpus.stopwords.words(lang)) for lang in nltk.corpus.stopwords.fileids()}
 
def get_language(text):
    words = set(nltk.wordpunct_tokenize(text.lower()))
    return max(((lang, len(words & stopwords)) for lang, stopwords in STOPWORDS_DICT.items()), key = lambda x: x[1])[0]
 
 
def is_english(text):
    text = text.lower()
    words = set(nltk.wordpunct_tokenize(text))
    # adding a requirement that at least one word found must be english
    # stopword. very naive way to do this, but worth a shot
    return len(words & ENGLISH_STOPWORDS) > len(words & NON_ENGLISH_STOPWORDS) \
            and len(words & ENGLISH_STOPWORDS) > 0

# /

def cleanStopWords(text):
    return filter(lambda word: word not in stopwords.words('english'),
            text.split(' '))

def isValidTweet(tweet):
    if tweet.get('text', -1) == -1:
        return False
    return True

#while True:
#    s = raw_input("Text:")
#    print is_english(s)

conn = Connection()
db = conn.tweets
old = db.raw
new = db.cleaned

for tweet in old.find():
    if isValidTweet(tweet) and is_english(tweet['text']):
        newText = ' '.join(cleanStopWords(tweet['text']))
        # print newText
        #print tweet
        tweet['cleanedText'] = newText
        new.insert(tweet)
        #TODO
        # old.remove({"_id" : {"$oid" : tweet['_id']}}) # nope..
