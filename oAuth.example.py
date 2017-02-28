from tweepy import OAuthHandler

#I reset these but you're free to pore through my git history for them
access_token = "???"
access_token_secret = "???"
consumer_key = "???"
consumer_secret = "???"

auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
