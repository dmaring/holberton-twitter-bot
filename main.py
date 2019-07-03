import os
from os import path
import sys
import tweepy
import requests
import json
import datetime
import dropbox
import random
import time
from tweepy.parsers import JSONParser
import tempfile
from werkzeug.utils import secure_filename

# dotenv used to import environment variables in development environment
from dotenv import load_dotenv
load_dotenv()

dbx = dropbox.Dropbox(os.getenv('DROPBOX_TOKEN'))

def get_file_path(filename):
    """Function to get the file path to temporarily store a photo"""

    file_name = secure_filename(filename)
    return os.path.join(tempfile.gettempdir(), file_name)

def setup_api():
    """Function to setup the tweepy twitter sdk api"""
    auth = tweepy.OAuthHandler(os.getenv('CONSUMER_KEY'),
                               os.getenv('CONSUMER_SECRET'))
    auth.set_access_token(os.getenv('ACCESS_TOKEN'),
                          os.getenv('ACCESS_TOKEN_SECRET'))

    return tweepy.API(auth, parser=JSONParser())

def get_tweet_time(api):
    """Function that finds the time of my last tweet"""

    most_recent_tweet = api.user_timeline(screen_name='drewmaring', count=1)
    tweet_time = most_recent_tweet[0]['created_at']
    return(tweet_time)

def check_date(tweet_time):
    """A function that compares my last tweet time with today's date"""

    # get today's date
    today = datetime.datetime.now() + datetime.timedelta(hours=-7)
    print("Today is {}".format(today));
    # print(today)
    # tweet date is
    tweet_date = datetime.datetime.strptime(tweet_time, "%a %b %d %X %z %Y")
    # correct time for utc
    tweet_date = tweet_date + datetime.timedelta(hours=-7)
    # print(tweet_date)

    # compare current date to tweet_date
    print("Today's date is: {}".format(today.date()))
    print("Tweets's date is: {}".format(tweet_date.date()))
    if today.date() == tweet_date.date():
        return(True)

def get_riley_photo():
    """
    Function that returns a random riley photo url and moves
    that photo to a 'tweeted' folder
    """

    riley_photos = []
    for entry in dbx.files_list_folder('/Public/riley_public').entries:
        riley_photos.append(entry.path_lower)
    random_riley_url = random.choice(riley_photos)
    print(random_riley_url)
    temp_file_path = get_file_path('temp.jpg')
    print(temp_file_path)
    meta_data = dbx.files_download_to_file(temp_file_path, random_riley_url)
    file_name = (os.path.split(random_riley_url))[1]
    dbx.files_move(random_riley_url,
                   ('/Public/riley_tweeted/{}'.format(file_name)))
    return(temp_file_path)

def get_kanye_quote():
    """Function that retrieves a random Kanye West Quote"""

    kanye_quote = requests.get('https://api.kanye.rest/')
    kanye_quote = kanye_quote.json()
    kanye_quote = kanye_quote['quote']
    kanye_quote = ('I forgot to tweet today. Enjoy this Kanye West quote ' +
    'and apologies for any profanity.\n "{}"').format(kanye_quote)
    return(kanye_quote)

def post_riley_tweet():
    """Function that tweets a random Riley photo"""

    message = ""
    api = setup_api()
    filename = get_riley_photo()
    print(filename)
    status = api.update_with_media(filename, status=message)

def post_tweet():
    """Function that decides what kind of content to tweet"""
    tweet_function = random.choice([
        post_riley_tweet
        ])
    tweet_function()

def post_new_tweet(request=None):
    """Main function for the twitterbot"""

    api = setup_api()
    tweet_time = get_tweet_time(api)

    if check_date(tweet_time):
        print("You tweeted today!")
        return("You tweeted today!")
    else:
        post_tweet()
        print("You did not tweet today! Tweet posted!")
        return("You did no tweet today! Tweet posted!")


if __name__ == '__main__':
    post_new_tweet()
