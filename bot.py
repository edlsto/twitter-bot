import tweepy
import requests
import os
import psycopg2
import datetime
import re
import logging
from bs4 import BeautifulSoup
from db_utils import get_random_photo, record_posted_image
from string_utils import get_first_sentence, get_sentences, extract_date
from date_utils import get_current_holiday
from generate_tweet_summary import generate_tweet_summary
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

TWEET_MAX_LENGTH = 280
URL_LENGTH = 23
DESCRIPTION_MAX_LENGTH = TWEET_MAX_LENGTH - URL_LENGTH

use_ai = True

def post_tweet_with_photo(post_data, twitter_API, client, con):
    image_page_url = post_data['image_page_url']
    summary = post_data['summary']
    date = post_data['date']
    image_path = post_data['image_path']
    photo_id = post_data['photo_id']
    
    try:
        media = twitter_API.media_upload(image_path)
        tweet = f"{summary} {date} {image_page_url}"
        logging.info(f"tweet: {tweet}")
        response = client.create_tweet(text=tweet, media_ids=[media.media_id])
        logging.info(f"Tweet made: {tweet}")

        record_posted_image(con, photo_id)

        return response
    except Exception as e:
        logging.error(f"Error posting tweet: {e}")
        return None

def fetch_image_page(image_page_url):
    try:
        response = requests.get(image_page_url)
        response.raise_for_status()
        return response.content
    except requests.RequestException as e:
        logging.error(f"Error fetching image page: {e}")
        return None

def get_image_url(image_page_content):
    soup = BeautifulSoup(image_page_content, 'html.parser')
    viewport_div = soup.find('div', id='viewport')
    if viewport_div:
        img_tag = viewport_div.find('img')
        if img_tag:
            return f'https://digital.denverlibrary.org/assets/display/{img_tag.get("idx")}-max'
    logging.warning("Image tag or viewport div not found.")
    return None

def download_image(img_url, idx_value):
    try:
        response = requests.get(img_url)
        response.raise_for_status()
        with open(f"./{idx_value}-max", 'wb') as file:
            file.write(response.content)
        return True
    except requests.RequestException as e:
        logging.error(f"Error downloading image: {e}")
        return False

def is_holiday_image(photo):
    holidays_keywords = ["Christmas", "Halloween", "New Year's", "Easter", "Fourth of July", "Thanksgiving"]
    summary = photo.get('summary', '').lower()
    subject = photo.get('subject', '').lower()
    
    return any(holiday.lower() in summary or holiday.lower() in subject for holiday in holidays_keywords)

def main():
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

    now = datetime.datetime.now()

    holiday = get_current_holiday()

    if holiday:
        if now.hour % 4 == 0:
            result = get_random_photo(con, holiday)
            logging.info(f"Posting holiday tweet for {holiday}.")
            if result is None:
                result = get_random_photo(con, holiday)
        else:
            result = get_random_photo(con)
            logging.info("Posting regular tweet.")
    else:
        # Non-holiday period: exclude holiday-related images
        while True:
            result = get_random_photo(con)
            if result and not is_holiday_image(result):  # Check if the image is NOT holiday-related
                break  # Only proceed if it's not a holiday-related image
            logging.info("Skipping holiday image for regular tweet.")

    # Check if a result was returned
    if result is None:
        logging.warning("No photo found to post.")
    else:
        summary = result["summary"]
        id = result["nodeid"]
        logging.info(f"Random photo summary (photo id: {id}): {summary}")
        photo_id = result["nodeid"]
        image_page_url = f'https://digital.denverlibrary.org/nodes/view/{photo_id}'

        # Fetch the image page content
        image_page_content = fetch_image_page(image_page_url)
        if image_page_content:
            img_url = get_image_url(image_page_content)
            if img_url:
                idx_value = img_url.split('-')[1]  # Extract idx_value from the URL
                
                # Download the photo
                if download_image(img_url, idx_value):
                    date = extract_date(result["date"])

                    # add the length of the date, plus a space before and after date
                    summary_max_length = DESCRIPTION_MAX_LENGTH - (len(date) + 2)

                    try:
                        # Check if the summary is greater than 257 characters
                        if len(result["summary"]) > summary_max_length:
                            if use_ai:
                                # Attempt to generate a tweet summary using the OpenAI API
                                summary = generate_tweet_summary(result["nodetitle"], result["summary"], summary_max_length)
                                if not summary:
                                    logging.warning("Generated summary is None, falling back to the old method.")
                                    summary = get_sentences(result["summary"], summary_max_length)
                            else:
                                summary = get_sentences(result["summary"], summary_max_length)
                        else:
                            summary = result["summary"]
                    except Exception as e:
                        logging.error(f"Failed to generate tweet summary: {e}")
                        summary = get_sentences(result["summary"], summary_max_length)

                    post_data = {
                        'image_page_url': image_page_url,
                        'summary': summary,
                        'date': date,
                        'image_path': f"./{idx_value}-max",
                        'photo_id': photo_id
                    }

                    post_tweet_with_photo(post_data, twitter_API, client, con)

                    os.remove(f"./{idx_value}-max")
                    logging.info(f"Removed file: ./{idx_value}-max")

if __name__ == "__main__":
    main()