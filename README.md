# Twitter Bot 

[![Build Status](https://travis-ci.com/dhaitz/twitter-bot.svg?token=dNDGtapxsNESrm54LMG7&branch=master)](https://travis-ci.com/dhaitz/twitter-bot)
[![Python 3.7](https://img.shields.io/badge/python-3.7-blue.svg)](https://www.python.org/downloads/release/python-370/)

A bot that tweets from a txt file.
Written in Python, deployment via Travis-CI to Heroku.
Inspired by [heroku-twitter-bot](https://emcain.github.io/heroku-twitter-bot/).



## How it works
The file `tweets.txt` is read in (and optionally shuffled).
Every line becomes a tweet (long lines are split into tweet threads).

Tweeting starts when the bot starts running or at a certain time of the day, depending on whether the `START_HOUR` env variable is set.

Waiting time between tweets can be set via `WAIT_TIME_HOURS` env variable. If not set, the default is 24 hours. 

## How to run it

- Create a Twitter account and an accompanying developer account. 
In the dev portal, create an app to get the keys/tokens. 

- Sign up to [Heroku](https://heroku.com) and create an app.
Set the access keys for twitter as config vars (in the settings tab): `CONSUMER_KEY`, `CONSUMER_SECRET`, `ACCESS_TOKEN`, `ACCESS_TOKEN_SECRET`
Optionally also set `START_HOUR` and `WAIT_TIME_HOURS`. 
The `Procfile` tells Heroku which command to run when starting the app. 

- Sign up to [travis-ci.com](https://travis-ci.com) (.org?).
The `.travis.yml` file tells Travis to run the tests and, if successful, deploy to Heroku.
Therefore, the file must contain the Heroku app name and authentication info. 
If you have the Heroku and Travis CLI tools installed, this command generates the key and adds it to `.travis.yml`:


    travis encrypt $(heroku auth:token) --add deploy.api_key [--pro]
    
Add the `--pro` flag if you're using travis.com, not travis.org