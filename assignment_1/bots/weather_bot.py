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
  '''
  corrects any spelling mistakes with most likely suggested word

  Arguments:
  - message: the message provided

  Returns:
  - the corrected string
  '''
  spell_check.set_text(message)

  for mistake in spell_check:
    suggested = mistake.suggest()[0]
    mistake.replace(suggested)

  return spell_check.get_text()

def get_first_city(message: str) -> str:
  '''
  returns the first city in the message

  Arguments:
  - message: the message provided

  Returns:
  - a city if found else empty string
  '''

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
def weatherbot(payload):
  print(payload)
  '''gets the weather if message in payload contains a city'''

  # get event
  event = payload.get('event', {})
  message = event.get('text')

  # if the userid of last message is not this bot's and has content
  if event.get('subtype') != 'message_deleted' and bot_id != event.get('user') and message:

    # echo back message
    print(message)
    client.chat_postMessage(channel=event.get('channel'), text=message)
     
    # find a city
    city = get_first_city(message)
    if city:
      print(f'Getting weather for {city}')

      params = {'q': city, 'appid': os.environ['WEATHER_API_KEY']}
      response = requests.get(url, params)
      print(response.status_code, response.text)

      # on success
      if response.status_code == 200:
        json = response.json()
        weather = f'Today\'s outlook: {json["weather"][0]["main"]} - {json["weather"][0]["description"]}'
        temperature = f'Feels like {json["main"]["feels_like"]} with a humidity of {json["main"]["humidity"]}'

        client.chat_postMessage(channel=event.get('channel'), text=f'{weather}\n{temperature}')

      # no city found
      elif response.status_code == 404:
        client.chat_postMessage(channel=event.get('channel'), text='oops couldn\'t find the city')

      # catch-all
      else:
        client.chat_postMessage(channel=event.get('channel'), text='unknown error')

if __name__ == '__main__':
  app.run(debug=True)