## About
The contents of this repo are the AWS Lambda files that power [**@nosoupforyoubot**](https://twitter.com/nosoupforyoubot), an automated Twitter account that tweets images from the 1990s sitcom *Seinfeld*. The Python script can easily be adjusted to accomplish similar tasks.

[FFmpeg](https://ffmpeg.org/) was used to extract images from video files.

## tweets.csv format

| episode       | title         |
|---------------|---------------|
| S1E01_01.png  | Seinfeld      |
| S1E01_02.png  | Seinfeld      |
| ...           | ...           |
| S1E01_139.png | Seinfeld      |
| S1E02_01.png  | The Stake Out |
| ...           | ...           |

Each image file is stored in an AWS S3 bucket.

## lambda_function.py

Each tweet consists of an image, timestamp, episode number, episode title, and may have an episode metatitle:

- `convert_filename` converts the image filename pattern into readable strings like "01:23 S1E01"
- `extract_metatitle` uses a regular expression to handle unique filename formats for two-part episodes
- `get_random_episode` selects a random row from the csv file
- `lambda_handler` calls Twitter and S3 APIs, formats the caption, posts the image, and likes relevant tweets

More comprehensive documentation can be found in the code.

## AWS deployment

- Upload `lambda_function.py`, `tweets.csv`, and an empty folder named `tmp` to a Lambda function environment
- Save Twitter developer keys as enviroment variables in the Lambda configuration:
  - API_KEY
  - API_KEY_SECRET
  - ACCESS_TOKEN
  - ACCESS_TOKEN_SECRET
- Create a Lambda layer to import Twitter's tweepy library
- Add an EventBridge trigger to automatically run `lambda_function.py` at an interval
- Increase the default timeout configuration if the code needs more than 3s to run
- Reduce retry attempts configuration to 0 if timeout is desired after set number of seconds
