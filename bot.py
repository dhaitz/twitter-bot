import random
import tweepy
import logging
import os
import time


def create_api():
    consumer_key = os.getenv("CONSUMER_KEY")
    consumer_secret = os.getenv("CONSUMER_SECRET")
    access_token = os.getenv("ACCESS_TOKEN")
    access_token_secret = os.getenv("ACCESS_TOKEN_SECRET")

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    
    api = tweepy.API(auth, 
                     wait_on_rate_limit=True, 
                     wait_on_rate_limit_notify=True)
    try:
        api.verify_credentials()
    except Exception as e:
        logging.error("Error creating API", exc_info=True)
        raise e
    logging.info("API created")
    return api

def get_texts(shuffle=False):
    with open('tweet_short.txt', 'r') as f:
        lines = f.read().splitlines()
    
    if shuffle:
        random.shuffle(lines)

    return lines
    

def main():
    api = create_api()
    
    tweet_texts = get_texts(shuffle=True)
    
    while True:
        for text in tweet_texts:
            logging.info(text)
            call_return_status = api.update_status(text)
            logging.info(call_return_status)
            
            time.sleep(60*60*24)  # wait 24h

if __name__ == '__main__':
    main()
