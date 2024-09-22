import os
from openai import OpenAI
import logging

logging.basicConfig(level=logging.INFO)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_tweet_summary(nodetitle, summary, max_length=253):
    prompt = f"Reduce this summary to no more than {max_length} characters. \n\nSummary: {summary}:"

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
            tweet_summary = tweet_summary[:max_length]

        return tweet_summary
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return None  # Or handle it in a way that fits your application
