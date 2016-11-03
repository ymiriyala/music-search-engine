from flask import Flask, request
import requests
import tweepy
import urllib2
from bs4 import BeautifulSoup
from twitter_authentication import API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET
import json

app = Flask(__name__)

auth = tweepy.OAuthHandler(API_KEY, API_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

@app.route("/")
def index():
    print('testing\n')
    return "Hello. Welcome to Yash's music search engine project."
    

@app.route('/getTweet', methods = ['GET'])
def getTweet():
    query = request.args['artist']
    api = tweepy.API(auth, parser=tweepy.parsers.JSONParser())
    max_tweets = 1
    searched_tweets = api.search(q=query, count=max_tweets)
   # jsonData = json.loads(searched_tweets)
    return json.dumps(searched_tweets)


#artist

@app.route('/getArtistID', methods = ['GET'])
def getArtistID():
    artist = request.args['artist']
    artistf = replaceSpaces(artist)
    #testString = 'https://api.spotify.com/v1/search?query='+artist+'&type=artist'
    artistStringData = urllib2.urlopen('https://api.spotify.com/v1/search?query='+artistf+'&type=artist').read()
    artistJson = json.loads(artistStringData)
    #return json.dumps(artistJson)
    #return json.dumps(artistJson)
    id = artistJson['artists']['items'][0]['id']
    #print artistJson
    return id

@app.route('/getTopTrack', methods = ['GET'])
def getTopTrack():
    artist = request.args['artist']
    uid = getArtistID()

    topTrackString =  urllib2.urlopen('https://api.spotify.com/v1/artists/'+uid+'/top-tracks?country=US').read()
    topTrackJson = json.loads(topTrackString)
    topTrack = topTrackJson['tracks'][0]['album']['name']

    return topTrack

@app.route('/getWiki', methods = ['GET'])
def getWiki():
    artist = request.args['artist']
    artistf = replaceSpaces(artist)
    excerptString = getWikiExcerpt(artistf)
    if "REDIRECT" in excerptString:
        artist = getWikiRedirect(excerptString)
        artistf = replaceSpaces(artist)
        excerptString = getWikiExcerpt(artistf)

    return excerptString

@app.route('/getInfo', methods = ['GET'])  #-------main method----------
def getInfo():
    topTrack = getTopTrack()
    tweets = getTweet()
    wiki = getWiki()
    info = {'Top Track': topTrack, 'Tweets': tweets, 'Wiki': wiki}
    return json.dumps(info)

def getWikiExcerpt(artistf):
    wikiString =  urllib2.urlopen('https://en.wikipedia.org/w/api.php?action=query&titles='+artistf+'&prop=revisions&rvprop=content&format=json').read()
    wikiJson = json.loads(wikiString)
    id = wikiJson['query']['pages'].keys()[0]
    excerpt = wikiJson['query']['pages'][id]['revisions'][0]['*']
    excerptString = json.dumps(excerpt)
    return excerptString

def getWikiRedirect(excerptString):
    for index in xrange(13, len(excerptString)): #13 characters in is when redirect title starts
        if excerptString[index] == ']':
            return excerptString[13:index]
    return excerptString

def replaceSpaces(word):
    newWord = ''
    for char in word:
        if char == ' ' or char == '_':
            newWord += "%20"
        else:
            newWord += char
    return newWord



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)