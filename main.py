from tweepy.streaming import StreamListener
from tweepy import Stream
import tweepy
import json
import pprint as pr
from pymongo import MongoClient
from matplotlib import pyplot as plt
from FollowSpider import FollowSpider
from BasicAccount import BasicAccount
import time
import oAuth

def initDatabase(name):
	client = MongoClient()
	db = client.tweets;
	return db[name];


def spiderBehavior():
	auth = OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_token, access_token_secret)
	API = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True, compression=True);
	account = BasicAccount(API);
	spider = FollowSpider(API);
	try:
		spider.loadSpider();
		print("spider loaded successfully... resuming");
		time.sleep(2);
		try:
			print("resuming spider");
			spider.resumeSpider();
		except KeyboardInterrupt:
			print "interrupted!!!";
			spider.saveSpider();
	except IOError:
		print("failed to load spider...");
		print("creating new spider...");
		time.sleep(2);
		spider = FollowSpider(API);
		initial = account.getUserFrequencySearch(['numpy'], 100);
		try:
			spider.startSpider(initial);
		except KeyboardInterrupt:
			print "interrupted!!!";
			spider.saveSpider();
			
if __name__ == '__main__':
	#This handles Twitter authetification and the connection to Twitter Streaming API
	spiderBehavior();
	
	#l = StdOutListener(UsernameCounter(API))
	#stream = Stream(auth, l)
	#This line filter Twitter Streams to capture data by the keywords: 'python', 'javascript', 'ruby'
	#stream.filter(track=['python', 'javascript', 'ruby'])


































