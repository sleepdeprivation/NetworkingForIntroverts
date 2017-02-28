from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import tweepy
import json
import pprint as pr
from pymongo import MongoClient
from matplotlib import pyplot as plt
from FollowSpider import FollowSpider
from BasicAccount import BasicAccount
import time

#Variables that contains the user credentials to access Twitter API 
access_token = "405233890-AyOaC3V3jdIFIWmbsFV7qTflNumAUvBDGHPnh682"
access_token_secret = "VHAMHDrbQ7eYxlM5vQIKJcZn3Mof236ejWgQEWunoHBIv"
consumer_key = "W2thDMZFtxzCksYNEXha0Atc1"
consumer_secret = "7BHZtGFaFA697SUqdq1VwK42ZFkLQk2guKsoMU9LCQF8MalyVd"

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


































