import random
import tweepy
import logging
import os
import time
import datetime


MAX_TWEET_SIZE = 280

WAIT_TIME_HOURS_DEFAULT = 24
WAIT_TIME_HOURS = float(os.getenv("WAIT_TIME_HOURS", default=WAIT_TIME_HOURS_DEFAULT))

START_HOUR_DEFAULT = 10
START_HOUR = int(os.getenv('START_HOUR', default=START_HOUR_DEFAULT))


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


def get_texts(input_file: str, shuffle=False) -> list:

    with open(input_file, 'r') as f:
        texts = f.read().splitlines()

    if shuffle:
        random.shuffle(texts)

    return texts


def get_individual_tweets_from_text(text, max_length=MAX_TWEET_SIZE) -> list:

    words = text.split()

    # start string with first word, then begin loop on second
    tweet_number = 1
    new_tweet = f"{tweet_number}/0"

    for word in words:

        if len(new_tweet + ' ' + word + ' ...') < max_length:  # if tweet is short enough with word appended, keep appending
            new_tweet = new_tweet + ' ' + word
        else:
            yield new_tweet + ' ...'
            tweet_number += 1
            new_tweet = f"{tweet_number}/0 ... " + word
    yield new_tweet


def wait_until_certain_hour_to_start(start_hour: int) -> None:
    while datetime.datetime.now().hour != start_hour:
        logging.info("Current hour: {datetime.datetime.now().hour},  start hour: {start_hour}  -> waiting ...")
        time.sleep(30*60)   # wait half an hour, then check again
    logging.info("Current hour: {datetime.datetime.now().hour} ==  start hour: {start_hour}")


def main(wait_time_hours: int, input_file: str) -> None:
    api = create_api()

    texts = get_texts(input_file, shuffle=True)

    while True:
        for text in texts:

            try:

                logging.info(text)

                # single tweets can not be longer, so split into chunks
                if len(text) <= MAX_TWEET_SIZE:
                    tweets = [text]

                else:
                    tweets = list(get_individual_tweets_from_text(text))
                    tweets = [tweet.replace('/0', f'/{len(tweets)}') for tweet in tweets]

                tweet_id = None
                for tweet in tweets:

                    logging.info(tweet)

                    call_return_status = api.update_status(tweet, tweet_id)
                    logging.info(call_return_status)

                    tweet_id = call_return_status.id

                time.sleep(60*60*wait_time_hours)  # turn hours into seconds

            except tweepy.error.TweepError as e:
                logging.error(e)


if __name__ == '__main__':

    wait_until_certain_hour_to_start(start_hour=START_HOUR)

    main(wait_time_hours=WAIT_TIME_HOURS, input_file='tweet_short.txt')
