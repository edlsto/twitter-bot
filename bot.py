import tweepy
import requests
import os
import psycopg2
import datetime
import re
from db_utils import get_random_photo
# from credentials import CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET
from os import environ

CONSUMER_KEY = environ['CONSUMER_KEY']
CONSUMER_SECRET = environ['CONSUMER_SECRET']
ACCESS_KEY = environ['ACCESS_KEY']
ACCESS_SECRET = environ['ACCESS_SECRET']
DATABASE_URL = os.environ['HEROKU_POSTGRESQL_PINK_URL']

def get_first_sentence(string):
    m = re.search('^.*?[\.!;](?:\s|$)(?<=[^ ]{4,4}[\.!;]\s)', string + ' ')
    if m is not None:
        result = m.group(0).strip()
        return result
    else:
        return ""

def get_sentences(string):
    last_character = list(string)[-1]
    if last_character not in (';', '.', '!'):
      string = string + '.';
      
    result = ""
    char_count = 0

    while char_count <= 270:
        string = string.strip()
        sentence = get_first_sentence(string)
        sentence_length = len(sentence)

        if char_count + sentence_length <= 276 and len(string) > 0:
            result += sentence + ' '
            char_count += sentence_length
            string = string.replace(sentence, '', 1)
        else:
            break

    result.strip()

    result = s = list(result)
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

# con = psycopg2.connect(database="historic_photos", user="edwardstoner", password="", host="127.0.0.1", port="5432")

#v1 auth
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
twitter_API = tweepy.API(auth)

#v2 auth
client = tweepy.Client(
    consumer_key=CONSUMER_KEY, consumer_secret=CONSUMER_SECRET,
    access_token=ACCESS_KEY, access_token_secret=ACCESS_SECRET
)

# Get the current time. Tweet if it's an even hour
now = datetime.datetime.now()
if now.hour % 2 == 0:

    # Get a random photo
    result = get_random_photo(con)
    photo_id = result["id"]

    # Download the photo
    response = requests.get(result['imageurl'])
    if response.status_code == 200:
        with open(f"./{photo_id}.jpg", 'wb') as file:
            file.write(response.content)

    # Upload the photo to twitter
    media = twitter_API.media_upload(f"./{photo_id}.jpg")

    # Assemble the tweet
    date = extract_date(result["date"])
    summary = get_sentences(result["summary"])
    if len(summary + " " + date) > 280:
        summary = summary[:277 - (len(date) + 1)] + '...'

    tweet = summary + " " + date + " " + result['pageurl']

    # Tweet
    response = client.create_tweet(
        text=tweet,
        media_ids=[media.media_id]
    )

    # Remove the photo file
    os.remove(f"./{photo_id}.jpg")

    print(f"Tweet made: {tweet}")