import tweepy
import urllib.request
import os
import psycopg2
import time
import datetime

# from credentials import CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET
from os import environ
CONSUMER_KEY = environ['CONSUMER_KEY']
CONSUMER_SECRET = environ['CONSUMER_SECRET']
ACCESS_KEY = environ['ACCESS_KEY']
ACCESS_SECRET = environ['ACCESS_SECRET']
DATABASE_URL = os.environ['DATABASE_URL']

from db_utils import get_random_photo, add_shared_photo
con = psycopg2.connect(DATABASE_URL, sslmode='require')
# con = psycopg2.connect(database="postgres", user="postgres", password="", host="127.0.0.1", port="5432")


auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)

twitter_API = tweepy.API(auth)
tweets = twitter_API.user_timeline('colohistory', count=200, include_entities=True, tweet_mode='extended')
now = datetime.datetime.now()
if now.hour % 2 == 0
    result = get_random_photo(con)
    photo_id = result["id"]
    urllib.request.urlretrieve(result['imageurl'], f"./{photo_id}.jpg")
    media = twitter_API.media_upload(f"./{photo_id}.jpg")
    summary = result["summary"][:200]
    date = result["date"].split(" ")[0]
    tweet = summary + " (" + date + ") " + result['pageurl']
    add_shared_photo(con, result["id"])
    twitter_API.update_status(status=tweet, media_ids=[media.media_id])
    os.remove(f"./{photo_id}.jpg")