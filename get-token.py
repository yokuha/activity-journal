#!/usr/bin/env python
#
# Approach for accessing Strava data based on https://www.grace-dev.com/python-apis/strava-api
# Copyright (C) 2022 yokuha
import json
import requests
import webbrowser


# Initial Settings
client_id = '101535'
client_secret = 'ce9c2353e1be45d0ad661cdce118886d2ce688b1'
redirect_uri = 'http://localhost/'

# Authorization URL
request_url = f'http://www.strava.com/oauth/authorize?client_id={client_id}' \
    f'&response_type=code&redirect_uri={redirect_uri}' \
    f'&approval_prompt=force' \
    f'&scope=profile:read_all,activity:read_all'

# User prompt showing the Authorization URL asking for the code
print('Please authorize the app and copy&paste below the generated code!')
print('P.S: you can find the code in the URL')
webbrowser.open(request_url)
code = input('Insert the code from the url: ')

# Get the access token
token = requests.post(url='https://www.strava.com/api/v3/oauth/token',
                      data={'client_id': client_id,
                            'client_secret': client_secret,
                            'code': code,
                            'grant_type': 'authorization_code'})

# Save response
strava_token = token.json()
with open('strava_token.json', 'w') as outfile:
    json.dump(strava_token, outfile)
