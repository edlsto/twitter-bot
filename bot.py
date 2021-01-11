import tweepy
import urllib.request
import os
import psycopg2
import time

# from credentials import CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET
from os import environ
CONSUMER_KEY = environ['CONSUMER_KEY']
CONSUMER_SECRET = environ['CONSUMER_SECRET']
ACCESS_KEY = environ['ACCESS_KEY']
ACCESS_SECRET = environ['ACCESS_SECRET']
DATABASE_URL = os.environ['DATABASE_URL']

from db_utils import get_random_photo
con = psycopg2.connect(DATABASE_URL, sslmode='require')

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)

result = get_random_photo(con)
photo_id = result["id"]
urllib.request.urlretrieve(result['imageurl'], f"images/{photo_id}.jpg")
twitter_API = tweepy.API(auth)
media = twitter_API.media_upload(f"images/{photo_id}.jpg")
summary = result["summary"][:200]
date = result["date"].split(" ")[0]
tweet = summary + " (" + date + ") " + result['pageurl']
twitter_API.update_status(status=tweet, media_ids=[media.media_id])
os.remove(f"images/{photo_id}.jpg")
print("done")
sys.stdout.flush()

