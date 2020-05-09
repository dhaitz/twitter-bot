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


# Twitter doesnt allow duplicate tweets.
# So, if we have reached the loop and are tweeting a text for the second time, we first have to delete the old tweet.
# The needed tweet IDs are tracked via this dict:
tweets_and_their_ids = {}


def run_bot(input_file: str, wait_time_hours: float) -> None:
    """Get texts from file, format into tweets, tweet and wait"""
    api = create_api()

    texts = get_texts(input_file, shuffle=True)

    while True:
        for text in texts:
            logging.info(text)
            tweets = get_individual_tweets_from_text(text)

            try:

                # For multiple tweets in a thread, we have to reply to the previous tweet via its id.
                # The first tweet replies to tweet id None -> not a reply
                id_of_thread_tweet_to_reply_to = None
                for tweet in tweets:

                    logging.info(tweet)

                    # remove old same tweet as duplicate tweets are not allowed by Twitter
                    if tweet in tweets_and_their_ids:
                        api.destroy_status(tweets_and_their_ids[tweet])

                    call_return_status = api.update_status(tweet, id_of_thread_tweet_to_reply_to)
                    logging.info(call_return_status)

                    id_of_thread_tweet_to_reply_to = call_return_status.id
                    tweets_and_their_ids[tweet] = call_return_status.id

                time.sleep(60*60*wait_time_hours)  # turn hours into seconds

            except tweepy.error.TweepError as e:
                logging.error(e)


def create_api() -> tweepy.API:
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
    """Check whether we can take the text as-is as tweet or have to split it into multiple tweets"""
    if len(text) <= max_length:
        tweets = [text]
    else:
        tweets = list(split_text_into_multiple_tweets(text, max_length))
        tweets = [tweet.replace('/0', f'/{len(tweets)}') for tweet in tweets]

    return tweets


def split_text_into_multiple_tweets(text: str, max_length: int = MAX_TWEET_SIZE) -> list:

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
    """Tweeting should start at a certain hour, not when the script starts"""
    while datetime.datetime.now().hour != start_hour:
        logging.info("Current hour: {datetime.datetime.now().hour},  start hour: {start_hour}  -> waiting ...")
        time.sleep(30*60)   # wait half an hour, then check again
    logging.info("Current hour: {datetime.datetime.now().hour} ==  start hour: {start_hour}")


if __name__ == '__main__':

    wait_until_certain_hour_to_start(start_hour=START_HOUR)

    run_bot(wait_time_hours=WAIT_TIME_HOURS, input_file='tweet_short.txt')
