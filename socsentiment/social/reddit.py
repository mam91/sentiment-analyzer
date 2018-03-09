import requests
import json
import time
import os
from nltk.sentiment.vader import SentimentIntensityAnalyzer as SIA
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
	def __init__(self, redditUser):
		self.user = redditUser
		self.analyze = SentimentAnalyzer()
	def get_posts(self, subreddit):
		try:
			endpointSub = subreddit.replace("http://www.reddit.com/","")
			hdr = {'User-Agent': 'windows:' + endpointSub + '.single.result:v1.0(by ' + self.user +')'}
			url = subreddit + '.json'
			req = requests.get(url, headers=hdr)
			json_data = json.loads(req.text)
	
			#posts = json.dumps(json_data['data']['children'], indent=4, sort_keys=True)
			data_all = json_data['data']['children']
			num_of_posts = 0
		
			while len(data_all) <= 100:
				time.sleep(2)
				last = data_all[-1]['data']['name']
				url = subreddit + '.json?after=' + str(last)
				req = requests.get(url, headers=hdr)
				data = json.loads(req.text)
				data_all += data['data']['children']
				if num_of_posts == len(data_all):
					break
				else:
					num_of_posts = len(data_all)
	
			return data_all
		except Exception as e:
			print("Error : " + str(e))

	def analyzeSentiment(self, subreddit):
		self.analyze.reset()
		data_all = self.get_posts(subreddit)

		for post in data_all:
			self.analyze.addString(post['data']['title'])

		sentiment = SentimentObject(self.analyze.getSentimentScore(),
									self.analyze.getVolume(),
									self.analyze.getPositivePercent(),
									self.analyze.getNegativePercent(),
									self.analyze.getNeutralPercent())
		return sentiment