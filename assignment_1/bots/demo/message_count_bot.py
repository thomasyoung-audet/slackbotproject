import os
import slack
import requests
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, request, Response
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

message_counts = {}

@ app.route('/message-count', methods=['POST'])
def message_count():
  data = request.form
  user_id = data.get('user_id')
  channel_id = data.get('channel_id')
  message_count = message_counts.get(user_id, 0)
  client.chat_postMessage(
    channel=channel_id, text=f"Message: {message_count}")
  print(message_counts)
  return Response(), 200

# handling Message Events
@slack_event_adapter.on('message')
def message(payload):
  print(payload)
  event = payload.get('event',{})
  user_id = event.get('user')

  if bot_id != user_id:
    if user_id in message_counts:
      message_counts[user_id] += 1
    else:
      message_counts[user_id] = 1

# Run the webserver micro-service
if __name__ == '__main__':
  app.run(debug=True)