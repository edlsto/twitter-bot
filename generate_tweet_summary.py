import os
from openai import OpenAI

client = OpenAI(api_key=os.environ.getenv("OPENAI_API_KEY"))

def generate_tweet_summary(nodetitle, summary, max_length=253):
    prompt = f"Generate a tweet summary from the following title and summary:\n\nTitle: {nodetitle}\nSummary: {summary}\n\nTweet Summary (max {max_length} characters):"

    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "user", "content": prompt}
            ],
            model="gpt-3.5-turbo"
        )

        tweet_summary = response['choices'][0]['message']['content'].strip()
        
        if len(tweet_summary) > max_length:
            tweet_summary = tweet_summary[:max_length]

        return tweet_summary
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return None  # Or handle it in a way that fits your application
