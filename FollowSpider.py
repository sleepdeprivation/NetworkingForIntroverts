from sets import Set
import thread
import time
import dill
import networkx as nx
import tweepy
import json
import pprint as pr
from collections import Counter

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
			
