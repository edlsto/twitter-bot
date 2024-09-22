import os
from openai import OpenAI
import logging
from string_utils import get_sentences
# from credentials import OPENAI_API_KEY

logging.basicConfig(level=logging.INFO)

# client = OpenAI(api_key=OPENAI_API_KEY)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_tweet_summary(nodetitle, summary, max_length=253):

    max_words = max_length // 8

    prompt = f"Please reduce the following photo caption to no more than {max_words} words. This is for a website about Colorado history. Keep as much relevant information as possible while ensuring you do NOT exceed the word limit.\n\nSummary: {summary}:"

    logging.info(f"Prompt: {prompt}")

    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "user", "content": prompt}
            ],
            model="gpt-4"
        )

        tweet_summary = response.choices[0].message.content.strip()

        logging.info(f"AI generated summary: {tweet_summary}")

        if len(tweet_summary) > max_length:
            tweet_summary = get_sentences(tweet_summary, max_length)

        return tweet_summary
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
