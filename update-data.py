#!/usr/bin/env python
#
# activity-journal -- create a journal of the notes of your own Strava activities.
# Copyright (C) 2023 yokuha
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


# getting, updating, saving the Strava token
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


# store Strava info in local json file
translation = {'name': 'name',
               'date': 'start_date',
               'note': 'description',
               'private_note': 'private_note',
               'AP': 'average_watts',
               'NP': 'weighted_average_watts',
               'calories': 'calories'
               }
def store(name, strava, local):
    if translation[name] in strava and len(str(strava[translation[name]])) > 0:
        local.update({name: strava[translation[name]]})



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


# get token data and update as necessary
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
athlete_id = athlete['id']
with open(f'{athlete_id}-athlete.json', 'w', encoding='utf-8') as db:
    json.dump(athlete, db, ensure_ascii=False, indent=4)

# define activities-filename
activities_file = f'{athlete_id}-activities.json'


# load already saved info
activities = {}
try:
    with open(activities_file, 'r', encoding='utf-8') as db:
        activities = json.load(db)
except FileNotFoundError:
    pass

# set up loading of activities -- for last n = 10 weeks
now = int(time.time()) + 10
week = 605000 # 604800 s to a week
before = now
after = now - week
page = 1
per_page = 100
for w in range(0, 30):
    # get activity list for that week
    print(f'getting data for week -{w}: epoch from {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(before))} to {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(after))}')
    activity_list_url = f"https://www.strava.com/api/v3/athlete/activities?access_token={access_token}&after={after}&before={before}&page={page}&per_page={per_page}"
    activity_list = requests.get(activity_list_url)
    print(f'fetched data for week -{w}: {str(activity_list)}')

    # get detailed activities and store in dictionary
    for i in range(len(activity_list.json())):
        activity_id = str(activity_list.json()[i]['id'])
        activity_url = f"https://www.strava.com/api/v3/activities/{activity_id}?access_token={access_token}"
        activity = requests.get(activity_url).json()
        try:
            assert int(activity_id) == activity['id']
            if activity_id not in activities:
                activities[activity_id] = {}
                for n in translation:
                    store(n, activity, activities[activity_id])
        except KeyError:
            print('KeyError .. continuing')

    # wait 15 min before fetching next week
    time.sleep(1000)
    after -= week
    before -= week

# save updated data
with open(activities_file, 'w', encoding='utf-8') as db:
    json.dump(activities, db, indent = 4)
