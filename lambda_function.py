import logging
import os
import requests

from flask import Flask, render_template
from flask_ask import Ask, request, session, question, statement, context

from satellite_pass import get_sats_above, get_fake_count, get_coordinates

app = Flask(__name__)
ask = Ask(app, "/")
logging.getLogger('flask_ask').setLevel(logging.DEBUG)

#
# Skill support
#

def get_alexa_location():
    # Get deviceId and accessToken
    deviceId = context.System.device.deviceId
    print("deviceId: {}".format(deviceId))
    accessToken = context.System.apiAccessToken
    print("accessToken: {}".format(accessToken))

    URL =  "https://api.amazonalexa.com/v1/devices/{}/settings" \
           "/address".format(deviceId)
    #TOKEN =  context.System.user.permissions.consentToken
    TOKEN = accessToken
    HEADER = {'Accept': 'application/json',
             'Authorization': 'Bearer {}'.format(TOKEN)}
    r = requests.get(URL, headers=HEADER)
    if r.status_code == 200:
        return(r.json())
    elif r.status_code == 403:
        # User hasn't enabled Address permissions
        return( { "FAIL": "FORBIDDEN" })
    else:
        print("status code: {}".format(r.status_code))
        return( { "FAIL": "OTHER"} )

def handle_forbidden():
    speech_text = render_template('fallback_address')
    card_title = render_template('card_title')
    return statement(speech_text).simple_card(card_title, speech_text)

def handle_other_failure():
    speech_text = render_template('other_failure')
    card_title = render_template('card_title')
    return statement(speech_text).simple_card(card_title, speech_text)

#
# Skill functionality
#


@ask.launch
def launch():
    return next_satellite_pass()

@ask.intent('NextSatellitePass')
def next_satellite_pass():
    location = get_alexa_location()
    # Test if request failed
    if "FAIL" in location:
        if location["FAIL"] == "FORBIDDEN":
            return handle_forbidden()
        else:
            return handle_other_failure()

    print("location: {}".format(location))

    coordinates = get_coordinates(location)

    sat_count = get_sats_above(coordinates.latitude, coordinates.longitude)

    # Handle partial address info
    loc_string = location['city']
    if loc_string is None or loc_string == "":
        loc_string = location['postalCode']
        speech_text = render_template('sats_above_postal', sat_count=sat_count, postal=loc_string)
    else:
        speech_text = render_template('sats_above', sat_count=sat_count, city=loc_string)
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