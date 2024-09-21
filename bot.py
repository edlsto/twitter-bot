import tweepy
import requests
import os
import psycopg2
import datetime
import re
import logging
from bs4 import BeautifulSoup
from db_utils import get_random_photo
# from credentials import CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET
from os import environ

logging.basicConfig(level=logging.INFO)

def get_env_var(name):
    value = os.environ.get(name)
    if value is None:
        logging.error(f"Missing environment variable: {name}")
        raise EnvironmentError(f"Missing environment variable: {name}")
    return value

CONSUMER_KEY = get_env_var('CONSUMER_KEY')
CONSUMER_SECRET = get_env_var('CONSUMER_SECRET')
ACCESS_KEY = get_env_var('ACCESS_KEY')
ACCESS_SECRET = get_env_var('ACCESS_SECRET')
DATABASE_URL = get_env_var('DATABASE_URL')

tweet_max_length = 280
url_length = 23
description_max_length = tweet_max_length - url_length;

def get_first_sentence(string):
    m = re.search('^.*?[\.!;](?:\s|$)(?<=[^ ]{4,4}[\.!;]\s)', string + ' ')
    if m is not None:
        result = m.group(0).strip()
        return result
    else:
        return ""

def get_sentences(string, max_length):
    last_character = list(string)[-1]
    if last_character not in (';', '.', '!'):
      string = string + '.';
      
    result = ""
    char_count = 0

    while char_count <= max_length:
        string = string.strip()
        sentence = get_first_sentence(string)
        sentence_length = len(sentence)

        if char_count + sentence_length <= max_length and len(string) > 0:
            result += sentence + ' '
            char_count += sentence_length
            string = string.replace(sentence, '', 1)
        else:
            break

    result = result.strip()

    result = s = list(result)
    if s[-1] == ';':
        s[-1] = '.'
    return "".join(s)

def extract_date(input_string):
    if input_string is None:
        return ''
    # Split the input string at the first semicolon
    parts = input_string.split(';', 1)
    
    # If there is a semicolon, return the part before it
    if len(parts) > 1:
        return f"({parts[0]})"
    else:
        # If there is no semicolon, return the original string
        return f"({input_string})"

# Function to check if the current date is between December 18th and December 25th
def is_within_xmas_period():
    now = datetime.datetime.now()
    return datetime.datetime(now.year, 12, 18) <= now <= datetime.datetime(now.year, 12, 25)

def post_tweet_with_photo(image_page_url, summary, date, twitter_API, client, media_file):
    try:
        media = twitter_API.media_upload(media_file)
        tweet = f"{summary} {date} {image_page_url}"
        response = client.create_tweet(text=tweet, media_ids=[media.media_id])
        logging.info(f"Tweet made: {tweet}")
        return response
    except Exception as e:
        logging.error(f"Error posting tweet: {e}")
        return None

try:
    con = psycopg2.connect(DATABASE_URL, sslmode='require')
except Exception as e:
    logging.error(f"Database connection error: {e}")
    raise
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

# Get a random Christmas photo
if now.hour % 4 == 0 and is_within_xmas_period():
    result = get_random_photo(con, "Christmas")

# Get a random photo
else:
    result = get_random_photo(con)

    photo_id = result["nodeid"]
    image_page_url = f'https://digital.denverlibrary.org/nodes/view/{photo_id}'
    image_page = requests.get(image_page_url)

    # Check if the request was successful
    if image_page.status_code == 200:
        soup = BeautifulSoup(image_page.content, 'html.parser')
        
        viewport_div = soup.find('div', id='viewport')
        if viewport_div:
            img_tag = viewport_div.find('img')
            if img_tag:
                idx_value = img_tag.get('idx')

                img_url = f'https://digital.denverlibrary.org/assets/display/{idx_value}-max'

                # Download the photo
                try:
                    response = requests.get(img_url)
                    if response.status_code == 200:
                        with open(f"./{idx_value}-max", 'wb') as file:
                            file.write(response.content)

                    # Assemble the tweet
                    date = extract_date(result["date"])

                    # add the length of the date, plus a space before and after date
                    summary_max_length = description_max_length - (len(date) + 2)
                    summary = get_sentences(result["summary"], summary_max_length)
                    
                    if len(summary) > summary_max_length:
                        summary = summary[:summary_max_length]

                    post_tweet_with_photo(image_url, summary, date, twitter_API, client, f"./{idx_value}-max")
                
                finally:
                    if os.path.exists(f"./{idx_value}-max"):
                        os.remove(f"./{idx_value}-max")
                        logging.info(f"Removed file: ./{idx_value}-max")

            else:
                logging.warning("No img tag found within viewport div.")
        else:
            logging.warning("Viewport div not found.")
    else:
        logging.error("Failed to retrieve the webpage. Status code:", image_page.status_code)