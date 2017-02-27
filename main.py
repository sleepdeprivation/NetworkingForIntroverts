#Import the necessary methods from tweepy library
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import tweepy
import json
from collections import Counter
import pprint as pr
from pymongo import MongoClient
import thread

#Variables that contains the user credentials to access Twitter API 
access_token = "405233890-AyOaC3V3jdIFIWmbsFV7qTflNumAUvBDGHPnh682"
access_token_secret = "VHAMHDrbQ7eYxlM5vQIKJcZn3Mof236ejWgQEWunoHBIv"
consumer_key = "W2thDMZFtxzCksYNEXha0Atc1"
consumer_secret = "7BHZtGFaFA697SUqdq1VwK42ZFkLQk2guKsoMU9LCQF8MalyVd"

def initDatabase(name):
	client = MongoClient()
	db = client.tweets;
	return db[name];

class FollowSpider():
	""""""
	def __init__(self, API):
		self.api = API;
		
	def recieveStream(self):
		pass
		
	def getFollowList(self):
		for status in tweepy.Cursor(self.api.user_timeline).items():
			pr.pprint(status._json);
			
class CompositeHandler():
	"""Handler to execute a list of handlers"""

	def __init__(self, handlers):
		self.handlers = handlers;
		
	def recieveStream(self, data):
		for f in handlers:
			f.recieveStream(data);
			
class Storage():
	"""Storage Handler"""
	def __init__(self, API, collection):
		self.api = API;
		self.collection = collection;

	def recieveStream(self, data):
		dat = json.loads(data);
		collection.insert(dat);
		
class UsernameCounter():
	def __init__(self, API):
		self.api = API;
		self.count = Counter();
		self.storeCount = 50;

	def recieveStream(self, data):
		dat = json.loads(data);
		pr.pprint(dat);
		print data.user;


class StdOutListener(StreamListener):
	"""engine for receiving streams"""
	def __init__(self, handler):
		self.handler = handler;

	def on_data(self, data):
		#print data;
		self.handler.recieveStream(data);
		return True

	def on_error(self, status):
		print status


class BasicAccount():

	def __init__(self, API):
		self.api = API;
		
	#Account destruction functions

	def deleteTweets(self):
		for status in tweepy.Cursor(self.api.user_timeline).items():
			self.api.destroy_status(status.id);
		
	def unfollowAll(self):
		for i in tweepy.Cursor(self.api.friends_ids).items():
			self.api.destroy_friendship(i);
	
	def forceUnfollowAll(self):
		for i in tweepy.Cursor(self.api.followers).items():
			self.forceUnfollowOn(i.id);

	def forceUnfollowOn(self, i):
		"""
		quickly block and then unblock the user
		with the given id to force them to unfollow you
		"""
		self.api.create_block(i);
		self.api.destroy_block(i);
		pass;
		
	def searchFollowingForKeywords(self, keywords):
		for i in tweepy.Cursor(self.api.friends_ids).items():
			for tl in tweepy.Cursor(self.api.user_timeline, i).items():
				pr.pprint(tl._json)
				returnValues = [];
			#for q in keywords:
			#	if(i.description.find(q) != -1):
			#		returnValues.apend(i['id']);
		#return returnValues
		
	def getKeywordHighFrequency(self, query):
		return tweepy.Cursor(self.api.search, q=query).items();
		
	def followHighFrequencySearch(self, query, freq, count):
		return self.followHighFrequency(self.getKeywordHighFrequency(query), freq, count);
			
	def followHighFrequency(self, CURSOR, freq, count):
		"""
			Run through the cursor `count` times and follow anyone mentioned
			more than `freq` times
		"""
		c = Counter();
		l = [];
		for i in CURSOR:
			#pr.pprint(i._json)
			pr.pprint(i.id);
			l.append(i.id);
			try:
				for mentioned in i.entities['user_mentions']:
					print("mention:");
					pr.pprint(mentioned['id']);
					l.append(mentioned['id']);
			except AttributeError:
				print "AttributeError loop 1";
			try:
				retweet_user = i['retweeted_status']['user']['id']
				print("retweet");
				pr.pprint(retweet_user);
				l.append(retweet_user);
			except TypeError:
				print "TypeError loop 2";
			if(count > 0):
				count-=1;
				print(count);
			else:
				break;
		c.update(l);
		print c;
		for key,val in c.most_common():
			if(val > freq):
				print("following ", key, val);
				API.create_friendship(key);
	

if __name__ == '__main__':

	#This handles Twitter authetification and the connection to Twitter Streaming API
	auth = OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_token, access_token_secret)
	API = tweepy.API(auth);
	account = BasicAccount(API);
	print account.followHighFrequencySearch(['numpy'], 5, 1000);

	#l = StdOutListener(UsernameCounter(API))
	#stream = Stream(auth, l)
	#This line filter Twitter Streams to capture data by the keywords: 'python', 'javascript', 'ruby'
	#stream.filter(track=['python', 'javascript', 'ruby'])


































