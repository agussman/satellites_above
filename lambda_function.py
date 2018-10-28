import logging
import os
from random import randint

from flask import Flask, render_template
from flask_ask import Ask, request, session, question, statement

from satellite_pass import get_sats_above, get_fake_count

app = Flask(__name__)
ask = Ask(app, "/")
logging.getLogger('flask_ask').setLevel(logging.DEBUG)

@ask.launch
def launch():
    return next_satellite_pass()

@ask.intent('NextSatellitePass')
def next_satellite_pass():

    sat_count = get_sats_above(38.99651, -77.320582)
    #sat_count = get_fake_count(38.99651, -77.320582)
    #speech_text = render_template('stub')
    speech_text = render_template('sats_above', sat_count=sat_count)
    card_title = render_template('card_title')
    return statement(speech_text).simple_card(card_title, speech_text)


@ask.intent('AMAZON.HelpIntent')
def help():
    help_text = render_template('help')
    return question(help_text).reprompt(help_text)


@ask.intent('AMAZON.StopIntent')
def stop():
    bye_text = render_template('bye')
    return statement(bye_text)


@ask.intent('AMAZON.CancelIntent')
def cancel():
    bye_text = render_template('bye')
    return statement(bye_text)


@ask.session_ended
def session_ended():
    return "{}", 200


if __name__ == '__main__':
    if 'ASK_VERIFY_REQUESTS' in os.environ:
        verify = str(os.environ.get('ASK_VERIFY_REQUESTS', '')).lower()
        if verify == 'false':
            app.config['ASK_VERIFY_REQUESTS'] = False
    app.run(debug=True)