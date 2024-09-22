import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_tweet_summary(nodetitle, summary, max_length=253):
    prompt = f"Generate a tweet summary from the following title and summary:\n\nTitle: {nodetitle}\nSummary: {summary}\n\nTweet Summary (max {max_length} characters):"

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    tweet_summary = response['choices'][0]['message']['content'].strip()
    
    if len(tweet_summary) > max_length:
        tweet_summary = tweet_summary[:max_length]

    return tweet_summary