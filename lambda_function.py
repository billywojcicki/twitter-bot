import boto3
import csv
import json
from pathlib import Path
import os
import random
import re
import tweepy


def convert_filename(filename):
    # Images were extracted from video files every 10 seconds
    # The following filename pattern was used:
    #
    #   S1E01_01.png
    #   S1E01_02.png
    #   ...
    #   S1E01_139.png
    #   S1E02_01.png
    #   ...
    #
    #
    #   The incrementing number after the underscore * 10
    #   == the number of seconds passed when the image was extracted
    
    # Get the number of seconds from the filename
    seconds = int(os.path.splitext(filename)[0].split("_")[-1]) * 10

    # Add random deviation to prevent all timestamps from being multiples of 10
    seconds = seconds + random.randint(-5, 5)

    # Convert the number of seconds into minutes and seconds
    minutes, seconds = divmod(seconds, 60)
    minutes_str = str(minutes).zfill(2)
    seconds_str = str(seconds).zfill(2)

    # Get the episode from the filename
    episode_number = filename.split("_")[0]

    # Format the minutes, seconds, and episode into a readable string
    readable_str = f"{minutes_str}:{seconds_str} {episode_number}"
    return readable_str



def extract_metatitle(title):
    # Two-part Seinfeld episodes share the same title,
    # resulting in nonstandard formats like "The Trip (Part 1)"
    
    # Regex to identify text inside parentheses
    match = re.search(r'(.*)\((.*)\)', title)

    # If the title contains parentheses
    if match:
        # Cut the parentheses and inner text into a separate string
        return match.group(1), " ("+match.group(2)+")"

    else:
        # If the title has no parentheses, just return it as is
        return title, ""



def get_random_tweet(tweets):
    # Create dictionary from tweets.csv with "episode" and "title" headers
    with open(tweets) as csv_file:
        reader = csv.DictReader(csv_file)
        csv_dict = [{"episode": row["episode"], "title": row["title"]} for row in reader]

    return random.choice(csv_dict)



def lambda_handler(event, context):
    # Get environment variables from AWS Lambda configuration
    # These keys and tokens can be found in the Twitter developer portal
    api_key = os.getenv("API_KEY")
    api_key_secret = os.getenv("API_KEY_SECRET")
    access_token = os.getenv("ACCESS_TOKEN")
    access_token_secret = os.getenv("ACCESS_TOKEN_SECRET")

    # Authenticate Twitter API
    # The tweepy library is not native to AWS Lambda, a custom layer is required
    auth = tweepy.OAuthHandler(api_key, api_key_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)

    # Get random episode strings from tweets.csv
    csv_row = get_random_tweet("tweets.csv")
    episode = csv_row["episode"]
    title = csv_row["title"]
    title, metatitle = extract_metatitle(title)

    # Download the selected image from the 'seinfeldframes' S3 bucket
    path = "/tmp/" + episode
    s3 = boto3.resource('s3')
    s3.Bucket('seinfeldframes').download_file(episode, path)

    # Format the caption and tweet the image
    media = api.media_upload(filename=path)
    api.update_status(status=convert_filename(episode) + ' "' + title + '"' + metatitle + ' #Seinfeld', media_ids=[media.media_id])
    return {"statusCode": 200, "episode": episode}