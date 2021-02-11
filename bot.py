import tweepy
import urllib.request
import os
import psycopg2
import time
import datetime
import re
from db_utils import get_random_photo
# from credentials import CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET
from os import environ

CONSUMER_KEY = environ['CONSUMER_KEY']
CONSUMER_SECRET = environ['CONSUMER_SECRET']
ACCESS_KEY = environ['ACCESS_KEY']
ACCESS_SECRET = environ['ACCESS_SECRET']
DATABASE_URL = os.environ['DATABASE_URL']

def get_first_sentence(string):
    m = re.search('^.*?[\.!;](?:\s|$)(?<=[^ ]{4,4}[\.!;]\s)', string + ' ')
    result = m.group(0).strip()
    s = list(result)
    if s[-1] == ';':
        s[-1] = '.'
    return "".join(s)

def extract_date(string):
    m = re.findall('(\d{4}\??)', string)
    if (len(m) == 1):
        result = m[0]
    elif (len(m) > 1):
        result = f"{m[0]}-{m[1]}"
    else:
        result = ''
    if re.findall('(?<=circa )(\d{4})', string):
        result = 'circa ' + result
    return f"({result})"

con = psycopg2.connect(DATABASE_URL, sslmode='require')
# con = psycopg2.connect(database="postgres", user="postgres", password="", host="127.0.0.1", port="5432")

#Authenticate to the Twitter API
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
twitter_API = tweepy.API(auth)

# Get the user timeline
tweets = []
for status in tweepy.Cursor(twitter_API.user_timeline, screen_name='@colohistory', tweet_mode="extended").items():
    tweets.append(status)
ids = []
for tweet in tweets:
    ids.append(tweet.entities['urls'][0]['expanded_url'].split("/")[-1])

# Get the current time. Tweet if it's an even hour
now = datetime.datetime.now()
if now.hour % 2 == 0:

    # Get a random photo
    result = get_random_photo(con, ids)
    photo_id = result["id"]

    # Download the photo
    urllib.request.urlretrieve(result['imageurl'], f"./{photo_id}.jpg")

    # Upload the photo to twitter
    media = twitter_API.media_upload(f"./{photo_id}.jpg")

    # Assemble the tweet
    date = extract_date(result["date"])
    summary = get_first_sentence(result["summary"])
    if len(summary + " " + date) > 280:
        summary = summary[:277 - (len(date) + 1)] + '...'

    tweet = summary + " " + date + " " + result['pageurl']

    # Tweet
    twitter_API.update_status(status=tweet, media_ids=[media.media_id])

    # Remove the photo file
    os.remove(f"./{photo_id}.jpg")

    print(f"Tweet made: {tweet}")