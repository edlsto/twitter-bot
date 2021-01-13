import tweepy
import urllib.request
import os
import psycopg2
import time
import datetime
import re

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

#Authenticate to the Twitter API
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
twitter_API = tweepy.API(auth)

def get_first_sentence(string):
    m = re.search('^.*?[\.!;\?](?:\s|$)', string)
    return m.group(0).strip()

# Get the user timeline
tweets = twitter_API.user_timeline('colohistory', include_entities=True, tweet_mode='extended')

# Get the current time. Tweet if it's an even hour
now = datetime.datetime.now()
if now.hour % 2 == 0:

    # Get a random photo
    result = get_random_photo(con)
    photo_id = result["id"]

    # Download the photo
    urllib.request.urlretrieve(result['imageurl'], f"./{photo_id}.jpg")

    # Upload the photo to twitter
    media = twitter_API.media_upload(f"./{photo_id}.jpg")
    
    # Assemble the tweet
    summary = get_first_sentence(result["summary"][:200])
    date = result["date"].split(" ")[0]
    tweet = summary + " (" + date + ") " + result['pageurl']
    
    # Add the photo to the shared_photos table in the database
    add_shared_photo(con, result["id"])

    # Tweet
    twitter_API.update_status(status=tweet, media_ids=[media.media_id])

    # Remove the photo file
    os.remove(f"./{photo_id}.jpg")