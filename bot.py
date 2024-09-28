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
# from credentials import CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET, DATABASE_URL, OPENAI_API_KEY
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

def twitter_auth():
    # v1 auth
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
    twitter_API = tweepy.API(auth)

    # v2 auth
    client = tweepy.Client(
        consumer_key=CONSUMER_KEY,
        consumer_secret=CONSUMER_SECRET,
        access_token=ACCESS_KEY,
        access_token_secret=ACCESS_SECRET
    )
    return twitter_API, client

def post_tweet_with_photo(post_data, twitter_API, client, con):
    image_page_url = post_data['image_page_url']
    summary = post_data['summary']
    date = post_data['date']
    image_path = post_data['image_path']
    photo_id = post_data['photo_id']
    
    try:
        media = twitter_API.media_upload(image_path)
        tweet = f"{summary} {date} {image_page_url}"
        response = client.create_tweet(text=tweet, media_ids=[media.media_id])
        logging.info(f"Tweet made: {tweet}")
        logging.info(f"Tweet length: {len(summary) + len(date) + 23 + 2} characters")
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
    holidays_keywords = ["Christmas", "New Year's", "Easter", "Fourth of July"]
    summary = photo.get('summary', '').lower()
    subject = photo.get('subject', '').lower()
    
    return any(holiday.lower() in summary or holiday.lower() in subject for holiday in holidays_keywords)

def get_holiday_photo(con, holiday, now):
    if now.hour % 4 == 0:
        result = get_random_photo(con, holiday)
        logging.info(f"In holiday period for {holiday}: Selected image for {holiday}.")
        if result is None:
            result = get_random_photo(con)
    else:
        result = get_random_photo(con)
        logging.info("In holiday period for {holiday}, but selected non-holiday image.")
    return result

def process_image_page(image_page_url):
    """
    Fetches the image page content and returns the image URL if found.
    """
    image_page_content = fetch_image_page(image_page_url)
    if not image_page_content:
        logging.warning(f"No content found for {image_page_url}")
        return None

    img_url = get_image_url(image_page_content)
    if not img_url:
        logging.warning("No image URL found.")
        return None
    
    return img_url

def handle_summary_length(result, summary_max_length, use_ai):
    """
    Handles the logic for checking summary length and generating or truncating it.
    Works directly with the `result` to access the summary, nodetitle, and date.
    """
    summary = result["summary"]
    
    try:
        if len(summary) > summary_max_length:
            logging.info(f"Summary length ({len(summary)} characters) exceeds max length ({summary_max_length} characters)")

            if use_ai:
                summary = generate_tweet_summary(result["nodetitle"], summary, result["date"], summary_max_length)
                if not summary:
                    logging.warning("Generated summary is None, falling back to truncation.")
                    return get_sentences(result["summary"], summary_max_length)

            return get_sentences(result["summary"], summary_max_length)
        
        return summary
    except Exception as e:
        logging.error(f"Failed to handle summary: {e}")
        return get_sentences(result["summary"], summary_max_length)

def post_image_tweet(result, img_url, image_page_url, idx_value, summary_max_length, use_ai, twitter_API, client, con):
    """
    Prepares and posts a tweet with an image.
    """
    date = extract_date(result["date"])
    summary = handle_summary_length(result, summary_max_length, use_ai)

    post_data = {
        'image_page_url': image_page_url,
        'summary': summary,
        'date': date,
        'image_path': f"./{idx_value}-max",
        'photo_id': result["nodeid"]
    }

    post_tweet_with_photo(post_data, twitter_API, client, con)
    os.remove(f"./{idx_value}-max")
    logging.info(f"Removed file: ./{idx_value}-max")

def process_and_post_image(result, image_page_url, use_ai, twitter_API, client, con):
    """
    Main function to process the image page and post the image tweet.
    """
    img_url = process_image_page(image_page_url)
    if not img_url:
        return

    idx_value = img_url.split('/')[-1].split('-')[0]

    # Download the image
    if not download_image(img_url, idx_value):
        logging.error(f"Failed to download image from {img_url}")
        return

    # Determine max length for summary
    date = extract_date(result["date"])
    summary_max_length = DESCRIPTION_MAX_LENGTH - (len(date) + 2)

    post_image_tweet(result, img_url, image_page_url, idx_value, summary_max_length, use_ai, twitter_API, client, con)

def connect_to_database():
    try:
        return psycopg2.connect(DATABASE_URL, sslmode='require')
    except Exception as e:
        logging.error(f"Database connection error: {e}")
        raise
    # con = psycopg2.connect(database="historic_photos", user="edwardstoner", password="", host="127.0.0.1", port="5432")

def get_photo_for_posting(con, now):
    holiday = get_current_holiday()

    if holiday and now.hour % 4 == 0:
        result = get_holiday_photo(con, holiday, now)
    else:
        # Exclude holiday-related images
        while True:
            result = get_random_photo(con)

            if result is None:
                logging.warning("No result found, breaking out of the loop.")
                break

            logging.info(f"Random photo: nodeid {result['nodeid']}")
            if result and not is_holiday_image(result):
                break
            logging.info("Skipping holiday image for regular tweet.")
    
    return result

def main():
    con = connect_to_database()

    # Authenticate for Twitter API
    twitter_API, client = twitter_auth()

    now = datetime.datetime.now()

    result = get_photo_for_posting(con, now)

    photo_id = result["nodeid"]
    image_page_url = f'https://digital.denverlibrary.org/nodes/view/{photo_id}'

    process_and_post_image(result, image_page_url, use_ai, twitter_API, client, con)

if __name__ == "__main__":
    main()
