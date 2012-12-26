from pymongo import Connection
import re
from guess_language import guess_language
from nltk.corpus import stopwords

def loadEmoticons(inpt_file):
    lst = []
    inpt = open(inpt_file)
    for line in inpt:
        lst.append(line.strip())
    return lst

# some test functions.
def isAtUsername(word):
    # matches if in form <anything>@<a-zA-Z0-9_><anthing>
    return re.match(".?@[a-zA-Z0-9_]*.?", word) != None

# TODO: decide if improvement needed.
def isURL(word):
    return re.match("http[s]*://", word) != None

def isEnglish(textList):
    guess = guess_language.guessLanguage(''.join(textList))
    if guess != 'en':
        return False
    return True

# cleaning functions.
# removes all characters that are not ascii.
def cleanUnlikeableCharacters(textList):
    newList = []
    for word in textList:
        newList.append("".join(i for i in word if ord(i)<128))
    return newList

def cleanEmoticons(textList):
    return [word if word not in EMOTICONS_LIST else '' for word in textList]

# TODO: test
# http://stackoverflow.com/questions/10072744/remove-repeating-characters-from-words
def cleanExtraLetters(textList):
    newList = []
    for word in textList:
        newList.append(reduce(lambda x,y: x+y if x[-2:]!=y*2 else x, word, ""))
    return newList

def cleanAtReply(textList):
    return [word if not isAtUsername(word) else 'USER' for word in textList]

def cleanURLs(textList):
    return [word if not isURL(word) else 'URL' for word in textList]

def cleanStopWords(textList):
    return filter(lambda word: word not in stopwords.words('english'), textList)

def isValidTweet(tweet):
    if tweet.get('text', -1) == -1:
        return False
    return True

# entry point
def connectAndClean():
    conn = Connection()
    db = conn.tweets
    old = db.raw
    new = db.cleaned

    for tweet in old.find():
        if isValidTweet(tweet):
            textList = tweet['text'].split(' ')
            textList = cleanAtReply(textList)
            textList = cleanURLs(textList)
            textList = cleanEmoticons(textList)
            textList = cleanUnlikeableCharacters(textList)
            if isEnglish(textList) and len(textList) > 0:
                textList = cleanExtraLetters(textList)
                textList = cleanStopWords(textList)
                newText = ' '.join(textList)
                print newText
            #tweet['cleanedText'] = newText
            #new.insert(tweet)
            # TODO
            #old.remove({"_id" : {"$oid" : tweet['_id']}}) # nope..

EMOTICONS_LIST = loadEmoticons('emoticons.txt')

if __name__ == '__main__':
    connectAndClean()
