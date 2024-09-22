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

from iicu_activity_journal import iicu
from iicu_activity_journal.iicu import activities_file, athlete_id, athlete_file, auth_key, item_names

@click.command()
@click.help_option('--help', '-h')
@click.option('-b', '--begin', 'a_begin', default=None, required=True,
              help='Beginning of date range for data download')
@click.option('-e', '--end', 'a_end', default='3333-12-31', required=False,
              help='End of date range for data download')
def main(a_begin, a_end):
    """Collect data from intervals.icu API for the activity journal"""

    # Get current athlete info and store locally
    response = requests.get(url = f'https://intervals.icu/api/v1/athlete/{athlete_id}/profile',
                            headers = {'Authorization': auth_key}, timeout=30)
    with open(athlete_file, 'w', encoding='utf-8') as db:
        json.dump(json.loads(response.text), db, indent=4)

    activities = {}
    # load already saved info
    try:
        with open(activities_file, 'r', encoding='utf-8') as db:
            activities = json.load(db)
    except FileNotFoundError:
        pass

    # Get the list of activities in date range
    data = json.loads(requests.get(url = f'https://intervals.icu/api/v1/athlete/{athlete_id}/activities?oldest={a_begin}&newest={a_end}',
                                   headers = {'Authorization': auth_key}, timeout=30).text)
    # extract logbook data and store in db
    for a in data:
        # Get notes of activity
        a['messages'] = json.loads(requests.get(url = f'https://intervals.icu//api/v1/activity/{a["id"]}/messages',
                                                headers = {'Authorization': auth_key}, timeout=30).text)
        if a['id'] not in activities:
            activities[a['id']] = {}
        for i in item_names.items():
            if i[1] in a:
                activities[a['id']].update({i[0]:a[i[1]]})

    # Get the list of notes in date range
    data = json.loads(requests.get(url = f'https://intervals.icu//api/v1/athlete/{athlete_id}/events?oldest={a_begin}&newest={a_end}T23:59:59',
                                   headers = {'Authorization': auth_key}, timeout=30).text)
    for a in data:
        if a['category'] in ['HOLIDAY', 'INJURED', 'NOTE', 'RACE_A', 'RACE_B', 'RACE_C'] \
           or a['category'] in ['WORKOUT'] and a['type'] == 'Other':
            if a['id'] not in activities:
                activities[a['id']] = {}
            for i in item_names.items():
                if i[1] in a:
                    activities[a['id']].update({i[0]:a[i[1]]})

    # save updated/current data
    with open(iicu.activities_file, 'w', encoding='utf-8') as db:
        json.dump(activities, db, indent=4)



if __name__ == "__main__":
    main(0,0)



### Local Variables:
### coding: utf-8
### truncate-lines: t
### End:
