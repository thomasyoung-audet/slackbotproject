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

url='https://geek-jokes.sameerkumar.website/api'
@app.route('/joke', methods=['GET','POST'])
def joke():
  data = request.form
  channel_id = data.get('channel_id')
  response = requests.request("GET", url)
  print(response.text)
  client.chat_postMessage(channel=channel_id, text=response.text)
  return Response(), 200

# Run the webserver micro-service
if __name__ == '__main__':
  app.run(debug=True)