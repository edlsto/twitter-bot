import tweepy
import requests
import os
import psycopg2
import datetime
import re
from bs4 import BeautifulSoup
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

    while char_count <= 257:
        string = string.strip()
        sentence = get_first_sentence(string)
        sentence_length = len(sentence)

        if char_count + sentence_length <= 257 and len(string) > 0:
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
                    response = requests.get(img_url)
                    if response.status_code == 200:
                        with open(f"./{idx_value}-max", 'wb') as file:
                            file.write(response.content)

                    # Upload the photo to twitter
                    media = twitter_API.media_upload(f"./{idx_value}-max")

                    # Assemble the tweet
                    date = extract_date(result["date"])

                    summary = get_sentences(result["summary"])
                    if len(summary + " " + date) > 257:
                        summary = summary[:257 - (len(date  + '...') + 1)]

                    tweet = summary + " " + date + " " + image_page_url

                    print(f"Assembled tweet: {tweet}")

                    # Tweet
                    response = client.create_tweet(
                        text=tweet,
                        media_ids=[media.media_id]
                    )

                    # Remove the photo file
                    os.remove(f"./{idx_value}-max")

                    print(f"Tweet made: {tweet}")

                else:
                    print("No img tag found within viewport div.")
            else:
                print("Viewport div not found.")
        else:
            print("Failed to retrieve the webpage. Status code:", image_page.status_code)