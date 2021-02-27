#########################################
#                                       #
#          Slack Bot WEATHER            #
#                                       #
#########################################

import os
import slack
import requests
from flask import Flask

import re
import spacy
import truecase
import geonamescache
from enchant.checker import SpellChecker

from pathlib import Path
from dotenv import load_dotenv
from slackeventsapi import SlackEventAdapter

# setup paths
env = Path('.') / '.env'
load_dotenv(dotenv_path=env)

# setup flask
app = Flask(__name__)
slack_event_adapter = SlackEventAdapter(os.environ['SIGNING_SECRET'], '/slack/events', app)

# setup slack
client = slack.WebClient(token=os.environ['SLACK_TOKEN'])
bot_id = client.api_call('auth.test')['user_id']

# setup nlu
spell_check = SpellChecker('en_US')
nlp = spacy.load('en_core_web_sm')
gc = geonamescache.GeonamesCache()  

def correct(message: str) -> str:
  spell_check.set_text(message)

  for mistake in spell_check:
    suggested = mistake.suggest()[0]
    mistake.replace(suggested)

  return spell_check.get_text()

def get_first_city(message: str) -> str:
  corrected = correct(message)
  true_case = truecase.get_true_case(corrected)
  doc = nlp(true_case)

  for ent in doc.ents:
    if ent.label_ in ['GPE', 'PERSON']:
      city = gc.get_cities_by_name(ent.text)
      if city:
        return ent.text

  return ''
      
url = 'http://api.openweathermap.org/data/2.5/weather?'
@slack_event_adapter.on('message')
def get_weather(payload):
  event = payload.get('event', {})

  if bot_id != event.get('user'):
    client.chat_postMessage(channel=event.get('channel'), text=event.get('text'))      

    city = get_first_city(event.get('text'))
    if city:
      params = {'q': city, 'appid': os.environ['WEATHER_API_KEY']}
      response = requests.get(url, params)

      if response.status_code == 200:
        client.chat_postMessage(channel=event.get('channel'), text=response.text)
      elif response.status_code == 404:
        client.chat_postMessage(channel=event.get('channel'), text='oops couldn\'t find the city')
      else:
        client.chat_postMessage(channel=event.get('channel'), text='unknown error')

if __name__ == '__main__':
  app.run(debug=True)
