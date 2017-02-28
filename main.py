#Import the necessary methods from tweepy library
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import tweepy
import json
from collections import Counter
import pprint as pr
from pymongo import MongoClient
import networkx as nx
from sets import Set
import thread
import time
import dill
from matplotlib import pyplot as plt

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
		self.G=nx.DiGraph();
		self.seen = Set();
		self.counter = Counter();
		
	def getFollowListFirstPage(self, identifier):
		"""Just want the first page of following, to avoid getting trapped"""
		cur = tweepy.Cursor(self.api.friends_ids, id=identifier).pages(1);#.items()
		return [i for i in cur];
		
	def addToGraph(self, identifier):
		"""
			Have we seen this user before?
			If not, go through it's followers and add them to the count
		"""
		if(identifier not in self.seen):
			self.seen.add(identifier);
			self.G.add_node(identifier);
			for page in self.getFollowListFirstPage(identifier):
				for i in page:
					print(identifier, i);
					self.counter[identifier] += 1;
					self.G.add_node(i);
					self.G.add_edge(identifier, i);
			return True;
		else:
			return False;
				
	def processNextUser(self):
		"""
			go through the most common users and add
			everyone they follow to the graph
			keep trying until we find one that hasn't been seen
		"""
		for i in self.counter.most_common():
			if(self.addToGraph(str(i[0]))):
				#graph is too big :(
				#nx.drawing.nx_pydot.write_dot(self.G, "g.dot")
				#plt.figure();
				#nx.draw(self.G);
				#print("plotting...");
				#plt.savefig("graph.png")#(block=False);
				break;
			else:
				continue;
		print("Completed");
		
	def startSpider(self, counter):
		"""
			Loop forever adding more nodes to graph
		"""
		self.counter = counter;
		while(True):
			self.processNextUser();
			self.saveSpider();
			print("sleeping...");
			time.sleep(60);
			
	def resumeSpider(self):
		print("called resume");
		time.sleep(2);
		self.startSpider(self.counter);
			
	def saveSpider(self):
		"""
			No free lunch when it comes to saving and loading :(
			
			self.G=nx.DiGraph();
			self.seen = Set();
			self.counter = Counter();
		
		"""
		print("saving spider...");
		nx.write_gpickle(self.G, 'graph.gpickle');
		with open('seen.dill', 'wb') as file:
			dill.dump(self.seen, file);
		with open('counter.dill', 'wb') as file:
			dill.dump(self.counter, file);
				
	def loadSpider(self):
		print("loading spider...");
		self.G = nx.read_gpickle('graph.gpickle');
		with open('seen.dill', 'rb') as file:
			self.seen = dill.load(file);
		with open('counter.dill', 'rb') as file:
			self.counter = dill.load(file);
			
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
		
	def getKeywordSearchCursor(self, query):
		return tweepy.Cursor(self.api.search, q=query).items();
		
	def followHighFrequencySearch(self, query, freq, count):
		return self.followHighFrequency(self.getKeywordSearchCursor(query), freq, count);
		
	def getUserFrequencySearch(self, query, count):
		return self.getFrequentUsers(self.getKeywordSearchCursor(query), count);
		
	def getFrequentUsers(self, CURSOR, count):
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
		return c;
			
	def followFrequentUsers(self, CURSOR, freq, count):
		"""
			Run through the cursor `count` times and follow anyone mentioned
			more than `freq` times
		"""
		c = getFrequencyCounts(self, CURSOR, count);
		print c;
		for key,val in c.most_common():
			if(val > freq):
				print("following ", key, val);
				API.create_friendship(key);
	

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
	print("welcome to python ! haha ! programin is fun!!! lolz awesomesauce.jpg")
	#l = StdOutListener(UsernameCounter(API))
	#stream = Stream(auth, l)
	#This line filter Twitter Streams to capture data by the keywords: 'python', 'javascript', 'ruby'
	#stream.filter(track=['python', 'javascript', 'ruby'])


































