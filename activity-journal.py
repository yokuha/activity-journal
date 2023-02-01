#!/usr/bin/env python
#
# Approach for accessing Strava data based on https://www.grace-dev.com/python-apis/strava-api
# Copyright (C) 2022 yokuha
import json
import os
import requests
import time


# initial/basic access settings
client_id = '101535'
client_secret = 'ce9c2353e1be45d0ad661cdce118886d2ce688b1'
redirect_uri = 'http://localhost/'



def request_token(client_id, client_secret, code):
    response = requests.post(url='https://www.strava.com/oauth/token',
                             data={'client_id': client_id, 'client_secret':
                                   client_secret, 'code': code, 'grant_type':
                                   'authorization_code'})
    return response



def refresh_token(client_id, client_secret, refresh_token):
    response = requests.post(url='https://www.strava.com/api/v3/oauth/token',
                             data={'client_id': client_id,
                                   'client_secret': client_secret,
                                   'grant_type': 'refresh_token',
                                   'refresh_token': refresh_token})
    return response



def write_token(token):
    with open('strava_token.json', 'w') as outfile:
        json.dump(token, outfile)



def get_token():
    with open('strava_token.json', 'r') as token:
        data = json.load(token)
    return data



# make sure we have a Strava token
if not os.path.exists('./strava_token.json'):
    request_url = f'http://www.strava.com/oauth/authorize?client_id={client_id}' \
                  f'&response_type=code&redirect_uri={redirect_uri}' \
                  f'&approval_prompt=force' \
                  f'&scope=profile:read_all,activity:read_all'
    print('Please authorize the app and copy&paste below the generated code!')
    print('P.S: you can find the code in the redirect URL after you authorized Strava in the browser')
    webbrowser.open(request_url)
    code = input('Insert the code from the url: ')
    token = request_token(client_id, client_secret, code)

    # Save json response as a variable
    strava_token = token.json()
    # Save tokens to file
    write_token(strava_token)


# get token data, updating as necessary
data = get_token()
if data['expires_at'] < time.time():
    print('Refreshing token')
    new_token = refresh_token(client_id, client_secret, data['refresh_token'])
    strava_token = new_token.json()
    # Update the file
    write_token(strava_token)
data = get_token()
access_token = data['access_token']

# get athlete
athlete_url = f"https://www.strava.com/api/v3/athlete?access_token={access_token}"
response = requests.get(athlete_url)
athlete = response.json()
print('Athlete info')
print('Name:', athlete['firstname'], '"' + athlete['username'] + '"', athlete['lastname'])
print('Gender:', athlete['sex'])
print('City:', athlete['city'], athlete['country'])
print('Timestap of athlete info:', athlete['created_at'])
print('-'*20)
# get activities
activity_list_url = f"https://www.strava.com/api/v3/athlete/activities?access_token={access_token}"
activity_list = requests.get(activity_list_url)
# activity = response.json()[5]
# print('='*5, 'SINGLE ACTIVITY', '='*5)
# print('Athlete:', athlete['firstname'], athlete['lastname'])
# print('Name:', activity['name'])
# print('Date:', activity['start_date'])
# print('Disance:', activity['distance'], 'm')
# print('Average Speed:', activity['average_speed'], 'm/s')
# print('Max speed:', activity['max_speed'], 'm/s')
# print('Moving time:', round(activity['moving_time'] / 60, 2), 'minutes')
# print('Location:', activity['location_city'], activity['location_state'], activity['location_country'])

# get detailed activities and print info
print(f'\n\n# activities:{len(activity_list.json())}\n')
for i in range(len(activity_list.json())):
    activity_id = activity_list.json()[i]['id']
    activity_url = f"https://www.strava.com/api/v3/activities/{activity_id}?access_token={access_token}"
    activity = requests.get(activity_url).json()
    print('\n')
    print('Name:', activity['name'])
    print('Note:', activity['description'])
    if 'private_note' in activity:
        print('priv:', activity['private_note'])
