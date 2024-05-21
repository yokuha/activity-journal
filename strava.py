#!/usr/bin/env python
#
# Strav auhtorization and functionality functions
# Copyright (C) 2023,2024 yokuha <jokuha@icloud.com>
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program. If not, see <https://www.gnu.org/licenses/>.

import json
import os
import requests
import time
import webbrowser

from settings import *


# Strava info translation to local json file
translation = {'name': 'name',
               'date': 'start_date',
               'note': 'description',
               'private_note': 'private_note',
               'AP': 'average_watts',
               'NP': 'weighted_average_watts',
               'calories': 'calories'
               }


def check_create_token():
    """Make sure we have a local current Strava API token

    Checks if we have a Strava API token saved in the local json file and if
    there is non available goes through the manual webbroswer authentication to
    get a URL code as user input, requests an API token from it, and then stores
    this locally.

    :return: Strava API token
    """
    if not os.path.exists('./strava_token.json'):
        request_url = f'http://www.strava.com/oauth/authorize?client_id={client_id}' \
                      f'&response_type=code&redirect_uri={redirect_uri}' \
                      f'&approval_prompt=force' \
                      f'&scope=profile:read_all,activity:read_all'
        print('Please authorize the app and copy&paste below the generated code!')
        print('P.S: you can find the code in the redirect URL after you authorized Strava in the browser')
        webbrowser.open(request_url)
        code = input('Insert the code from the url: ')
        token = request_token(code)

        # Save json response as a variable
        strava_token = token.json()
        # Save tokens to file
        write_token(strava_token)
    return get_token()


def request_token(code):
    """Get a Strava API token

    This creates an access token for the (manually created) authorization code,
    stores it locally, and returns.

    :return: Strava API token
    """
    response = requests.post(url='https://www.strava.com/oauth/token',
                             data={'client_id': client_id, 'client_secret':
                                   client_secret, 'code': code, 'grant_type':
                                   'authorization_code'})
    print(f'Request-token response: {response}')
    return response


def refresh_token(refresh_token):
    """Refreshing the Strava API token

    :return: Strava API token
    """
    token = check_create_token()
    if token['expires_at'] < time.time():
        print('Refreshing token')
        response = requests.post(url='https://www.strava.com/api/v3/oauth/token',
                                 data={'client_id': client_id,
                                       'client_secret': client_secret,
                                       'grant_type': 'refresh_token',
                                       'refresh_token': refresh_token})
        new_token = refresh_token(client_id, client_secret, data['refresh_token'])
    strava_token = new_token.json()
    write_token(strava_token)
    return get_token()


def write_token(token):
    """Save Strava API token locally"""
    with open('strava_token.json', 'w') as outfile:
        json.dump(token, outfile)


def get_token():
    """Return locally stored Strava API token"""
    with open('strava_token.json', 'r') as token:
        data = json.load(token)
    return data


def store(name, strava, local):
    """Store value locally"""
    if translation[name] in strava and len(str(strava[translation[name]])) > 0:
        local.update({name: strava[translation[name]]})


def check_create_token():
    """Make sure we have a local current Strava API token

    Chekcs if we have a Strava API token saved in the local json file and if
    there is non available gors through the manual webbroswer authentication to
    get one as user input and then stores it locally.

    :return: Strava API token
    """
    if not os.path.exists('./strava_token.json'):
        request_url = f'http://www.strava.com/oauth/authorize?client_id={client_id}' \
                      f'&response_type=code&redirect_uri={redirect_uri}' \
                      f'&approval_prompt=force' \
                      f'&scope=profile:read_all,activity:read_all'
        print('Please authorize the app and copy&paste below the generated code!')
        print('P.S: you can find the code in the redirect URL after you authorized Strava in the browser')
        webbrowser.open(request_url)
        code = input('Insert the code from the url: ')
        token = request_token(code)

        # Save json response as a variable
        strava_token = token.json()
        # Save tokens to file
        write_token(strava_token)
    return get_token()



if '__main__' == __name__:
    print(check_create_token()['access_token'])




### Local Variables:
### coding: utf-8
### truncate-lines: t
### End:
