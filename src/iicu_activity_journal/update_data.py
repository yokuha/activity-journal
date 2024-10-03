#!/usr/bin/env python
#
# activity-journal -- create a journal of the notes of your own intervals.icu activities.
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


"""Collect data from intervals.icu API for the activity journal"""


import json

import click
import requests
import time

from iicu_activity_journal import iicu
from iicu_activity_journal.iicu import activities_file, athlete_id, athlete_file, auth_key, item_names
from iicu_activity_journal import validate


def iicu_data(request):
    """Request data from i.icu"""
    counter = 0
    while counter < 3:
        counter += 1
        response = requests.get(url=request, headers={'Authorization': auth_key}, timeout=30)
        if response.status_code == 200:
            # extract data and return
            return json.loads(response.text)
        elif response.status_code == 429:
            # i.icu rate limit reached – throttle and request again
            print(f'{request} timed out {counter}. time – sleeping')
            time.sleep(0.1)
            continue
        else:
            # unhandled error
            print(f'API-request {request} yielded error {response.status_code}')
            exit(-1)
            break
    print(f'API-request {request} repeatedly yielded error {response.status_code}')
    exit(-1)



@click.command()
@click.help_option('--help', '-h')
@click.option('-b', '--begin', 'a_begin', default=None, required=True,
              help='Beginning of date range for data download')
@click.option('-e', '--end', 'a_end', default='3333-12-31', required=False,
              help='End of date range for data download')
@click.option('-s', '--sort', 'a_sort', is_flag=True, default=False, show_default=True,
              help='Sort logbook entries for saving')
def main(a_begin, a_end, a_sort):
    """Collect data from intervals.icu API for the activity journal"""

    # Get current athlete info and store locally
    with open(athlete_file, 'w', encoding='utf-8') as db:
        json.dump(iicu_data(f'https://intervals.icu/api/v1/athlete/{athlete_id}/profile'), db, indent=4)

    activities = {}
    # load already saved info
    try:
        with open(activities_file, 'r', encoding='utf-8') as db:
            activities = dict(json.load(db, object_pairs_hook=validate.validate_data))
    except ValueError as err:
        print(err)
    except FileNotFoundError:
        pass

    # Get the list of activities in date range
    data = iicu_data(f'https://intervals.icu/api/v1/athlete/{athlete_id}/activities?oldest={a_begin}&newest={a_end}')
    # extract logbook data and store in db
    for a in data:
        a_id = str(a['id'])
        # Get notes of activity
        a['messages'] = iicu_data(f'https://intervals.icu//api/v1/activity/{a_id}/messages')
        if a_id not in activities:
            activities[a_id] = {}
        for i in item_names.items():
            if i[1] in a:
                activities[a_id].update({i[0]:a[i[1]]})

    # Get the list of notes in date range
    data = iicu_data(f'https://intervals.icu/api/v1/athlete/{athlete_id}/events?oldest={a_begin}&newest={a_end}')
    # extract logbook data and store in db
    for a in data:
        a_id = str(a['id'])
        if a['category'] in ['HOLIDAY', 'INJURED', 'NOTE', 'RACE_A', 'RACE_B', 'RACE_C']:
            if a_id not in activities:
                activities[a_id] = {}
            for i in item_names.items():
                if i[1] in a:
                    activities[a_id].update({i[0]:a[i[1]]})

    if a_sort:
        import datetime as dt
        activities = dict(sorted(activities.items(),
                                 key=lambda item: dt.datetime.fromisoformat(item[1]['date']),
                                 reverse=True))


    # save updated/current data
    with open(iicu.activities_file, 'w', encoding='utf-8') as db:
        json.dump(activities, db, indent=4)



if __name__ == "__main__":
    main(0,0)



### Local Variables:
### coding: utf-8
### truncate-lines: t
### End:
