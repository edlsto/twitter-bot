import tweepy
import time
import re
import urllib.request
import random
import ast
import os
import sqlite3

from credentials import CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET
from db_utils import get_random_photo
conn = sqlite3.connect('photos.db')

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)

while True:
    result = get_random_photo(conn)[0]
    photo_id = result["id"]
    urllib.request.urlretrieve(result['imageUrl'], f"images/{photo_id}.jpg")
    twitter_API = tweepy.API(auth)
    media = twitter_API.media_upload(f"images/{photo_id}.jpg")
    summary = result["summary"][:200]
    date = result["date"].split(" ")[0]
    tweet = summary + " (" + date + ") " + result['pageUrl']
    print(tweet)
    twitter_API.update_status(status=tweet, media_ids=[media.media_id])
    time.sleep(600)


