import os
import slack
from flask import Flask
from pathlib import Path
from dotenv import load_dotenv
from slackeventsapi import SlackEventAdapter

# load token from .env
env_path = Path(__file__).resolve().parents[1] / '.env'
load_dotenv(dotenv_path=env_path)

# configure flask
app = Flask(__name__)

# configure SlackEventAdapter
slack_event_adapter = SlackEventAdapter(os.environ['SIGNING_SECRET'], '/slack/events', app)

# create slack WebClient
client = slack.WebClient(token=os.environ['SLACK_TOKEN'])

# get botID
bot_id = client.api_call('auth.test')['user_id']

# handling Message Events
@slack_event_adapter.on('message')
def message(payload):
  print(payload)
  event = payload.get('event', {})
  channel_id = event.get('channel')
  user_id = event.get('user')
  msg = event.get('text')
  if bot_id != user_id:
    client.chat_postMessage(channel=channel_id, text=msg)

# Run the webserver micro-service
if __name__ == '__main__':
  app.run(debug=True)