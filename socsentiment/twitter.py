import requests
import json
import time
import os
from nltk.sentiment.vader import SentimentIntensityAnalyzer as SIA
import tweepy
from tweepy import OAuthHandler
from textblob import TextBlob
import re

def roundStr(numberToRound):
	return "{:.4f}".format(numberToRound) 

class SentimentObject(object):
	def __init__(self, sentiment, volume, positive, negative, neutral):
		self.sentiment = sentiment
		self.volume = volume
		self.positive = positive
		self.negative = negative
		self.neutral = neutral

class SentimentAnalyzer(object):
	def __init__(self):
		self.sia = SIA()
		self.positive_count = 0
		self.negative_count = 0
		self.neutral_count = 0
		self.volume = 0
		self.sentimentTotal = 0
		self.positive_threshold = 0.2
		self.negative_threshold = -0.2
		
	def addString(self, stringToAnalyze):
		res = self.sia.polarity_scores(stringToAnalyze)
		self.sentimentTotal = self.sentimentTotal + res['compound']
	
		if res['compound'] > self.positive_threshold:
			self.positive_count = self.positive_count + 1
		elif res['compound'] < self.negative_threshold:
			self.negative_count = self.negative_count + 1
		else:
			self.neutral_count = self.neutral_count + 1
			
		self.volume = self.volume + 1
		
	def reset(self):
		self.positive_count = 0
		self.negative_count = 0
		self.neutral_count = 0
		self.volume = 0
		self.sentimentTotal = 0
	
	def getVolume(self):
		return str(self.volume)
		
	def getSentimentScore(self):
		return roundStr(self.sentimentTotal / self.volume)

	def getPositivePercent(self):
		return roundStr(self.positive_count / self.volume * 100)

	def getNegativePercent(self):
		return roundStr(self.negative_count / self.volume * 100)

	def getNeutralPercent(self):
		return roundStr(self.neutral_count / self.volume * 100)

class Client(object):
	def __init__(self, key, secret, token, tokenSecret):
		self.analyze = SentimentAnalyzer()
		try:
			self.auth = OAuthHandler(key, secret)
			self.auth.set_access_token(token, tokenSecret)
			self.api = tweepy.API(self.auth)
		except:
			print("Error: Authentication Failed")

	def get_tweets(self, query, count = 10):
		tweets = []
		try:
			fetched_tweets = self.api.search(q = query, count = count)

			for tweet in fetched_tweets:
				parsed_tweet = {}

				parsed_tweet['text'] = tweet.text

				if tweet.retweet_count > 0:
					if parsed_tweet not in tweets:
						tweets.append(parsed_tweet)
				else:
					tweets.append(parsed_tweet)
			return tweets
		except tweepy.TweepError as e:
			print("Error : " + str(e))
			
	def analyzeSentiment(self, hashtag):
		self.analyze.reset()
		tweets = self.get_tweets(query = hashtag, count = 20000)
		
		for i in range(len(tweets)):
			self.analyze.addString(tweets[i]['text'])

		sentiment = SentimentObject(self.analyze.getSentimentScore(),
									self.analyze.getVolume(),
									self.analyze.getPositivePercent(),
									self.analyze.getNegativePercent(),
									self.analyze.getNeutralPercent())
		return sentiment