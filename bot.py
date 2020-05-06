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



def get_splitted_texts(s, max_tweet_size):

    words = s.split()

    # start string with first word, then begin loop on second
    tweet_number = 1
    new_tweet = f"{tweet_number}/0"

    for word in words:

        if len(new_tweet + ' ' + word + ' ...') < max_tweet_size:  # if tweet is short enough with word appended, keep appending
            new_tweet = new_tweet + ' ' + word
        else:
            yield new_tweet + ' ...'
            tweet_number += 1
            new_tweet = f"{tweet_number}/0 ... " + word
    yield  new_tweet


max_tweet_size = 280


def main(wait_time_hours):
    api = create_api()

    tweet_texts = get_texts(shuffle=True)

    while True:
        for text in tweet_texts:

            logging.info(text)

            # single tweets can not be longer, so split into chunks
            if len(text) <= max_tweet_size:
                chunks = [text]

                ##
                continue
                ##


            else:
                chunks = get_splitted_texts(text, max_tweet_size)
                chunks = list(chunks)
                chunks = [chunk.replace('/0', '/'+str(len(chunks))) for chunk in chunks]

            tweet_id = None
            for chunk in chunks:

                logging.info(chunk)
                call_return_status = api.update_status(chunk, tweet_id)

                tweet_id = call_return_status.id

                logging.info(call_return_status)

            time.sleep(60*60*wait_time_hours)  # wait 24h

if __name__ == '__main__':
    main(wait_time_hours=4)
