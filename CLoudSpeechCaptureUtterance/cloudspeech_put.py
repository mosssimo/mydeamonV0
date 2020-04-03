#!/usr/bin/env python3
# Copyright 2017 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""A demo of the Google CloudSpeech recognizer."""
import argparse
import locale
import logging
import requests

from aiy.board import Board, Led
from aiy.cloudspeech import CloudSpeechClient
from aiy.voice import tts

def get_hints(language_code):
    if language_code.startswith('en_'):
        return ('turn on the light',
                'turn off the light',
                'blink the light',
                'goodbye')
    return None

def locale_language():
    language, _ = locale.getdefaultlocale()
    return language

def main():
    tts.say('Hello Paul, how are you.',volume=20)
    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser(description='Assistant service example.')
    parser.add_argument('--language', default=locale_language())
    parser.add_argument('-u', '--url', help="The url for the server")
    args = parser.parse_args()
    api_url_base = args.url
    if api_url_base == "None":
        api_url_base = "http://localhost:3000"
    print(api_url_base)
    
    logging.info('Initializing for language %s...', args.language)
    hints = get_hints(args.language)
    client = CloudSpeechClient()
    with Board() as board:
        while True:
            if hints:
                logging.info('Say something, e.g. %s.' % ', '.join(hints))
                #tts.say('Say something, e.g. %s.' % ', '.join(hints))
            else:
                logging.info('Say something.')
                tts.say('Say something.',volume=20)
            text = client.recognize(language_code=args.language,
                                    hint_phrases=hints)
            if text is None:
                logging.info('You said nothing.')
                tts.say('You said nothing.',volume=20)
                continue
            
            # Post text
            parameters = {"utterance":text, "date":"","time":"","location":""}
            description = {"Content-Type":"application/json; charset=utf-8"}
            response = requests.post(api_url_base, json = parameters, headers = description)
            
            # Print and say text
            logging.info('You said: "%s"' % text)
            tts.say('You said, ' + text,volume=20)
            
            # Print data base
            response = requests.get(api_url_base)
            print(response)
            #print(response.text)
            
            text = text.lower()
            if 'turn on the light' in text:
                board.led.state = Led.ON
            elif 'turn off the light' in text:
                board.led.state = Led.OFF
            elif 'blink the light' in text:
                board.led.state = Led.BLINK
            elif 'goodbye' in text:
                break

if __name__ == '__main__':
    main()
