
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

