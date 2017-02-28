from collections import Counter
import json
import pprint as pr
import tweepy

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
	
