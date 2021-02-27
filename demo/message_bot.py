import os
import slack
from pathlib import Path
from dotenv import load_dotenv

# load token from .env
env_path = Path(__file__).resolve().parents[1] / '.env'
load_dotenv(dotenv_path=env_path)

# create slack WebClient
client = slack.WebClient(token=os.environ['SLACK_TOKEN'])

# connect the bot to the channel
client.chat_postMessage(channel='bot', text='Send Message Demo')