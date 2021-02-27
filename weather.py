#########################################
#                                       #
#          Slack Bot WEATHER            #
#                                       #
#########################################

import os
import slack
import requests
from flask import Flask

from pathlib import Path
from dotenv import load_dotenv
from urllib.parse import urlencode
from slackeventsapi import SlackEventAdapter

# setup
env = Path('.') / '.env'
load_dotenv(dotenv_path=env)

app = Flask(__name__)
slack_event_adapter = SlackEventAdapter(os.environ['SIGNING_SECRET'], '/slack/events', app)
client = slack.WebClient(token=os.environ['SLACK_TOKEN'])

bot_id = client.api_call('auth.test')['user_id']

url = 'http://api.openweathermap.org/data/2.5/weather?'
# handle message events
@slack_event_adapter.on('message')
def echo(payload):
  event = payload.get('event', {})

  if bot_id != event.get('user'):
    params = {'q': event.get('text'), 'appid': os.environ['WEATHER_API_KEY']}
    response = requests.get(url, params)
    
    if response.status_code == 200:
      client.chat_postMessage(channel=event.get('channel'), text=response.json())      
    else:
      client.chat_postMessage(channel=event.get('channel'), text=response.text)

if __name__ == '__main__':
  app.run(debug=True)
