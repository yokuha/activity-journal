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

# For API details, see
# https://developers.strava.com/docs/reference/#api-Activities-createActivity

import click, datetime,time
import requests
import strava

@click.command()
@click.help_option('--help', '-h')
@click.option('-n', '--name', 'a_name', default=None,
              help='Name of ativity')
@click.option('-k', '--kind', '--sporttype', 'a_type', default='Workout',
              help='Sport type of activity, e.g., Ride, Run, Workout, etc. (default: Workout)')
@click.option('-d', '--date', 'a_date', default=None,
              help='Checkout repo of new project into CWD. (default: today)')
@click.option('-t', '--time', 'a_time', default=None,
              help='Start time of activity in hh:mm. (default: now - duration)')
@click.option('-e', '--ellapsed', 'a_ellapsed', default=60,
              help='Elapsed time of activity in min (default: 1 h).')
@click.option('-i', '--info', '--description', 'a_description', default='',
              help='Description info for activity (default: <empty>).')
def main(a_name, a_type, a_date, a_time, a_ellapsed, a_description):
    # convert duration from input in minutes to seconds
    a_ellapsed *= 60
    # create a datetime object from date and time
    if not a_date:
        a_date = datetime.date.today()
    else:
        a_date = datetime.datetime(*map(int, a_date.split('-')))
    if not a_time:
        a_time = datetime.datetime.now() - datetime.timedelta(seconds=a_ellapsed)
    else:
        hh, mm = a_time.split(':')
        a_time = datetime.datetime(a_date.year, a_date.month, a_date.day, int(hh), int(mm))

    # Create the Activity
    api_token = strava.refresh_token()['access_token']
    response = requests.post(url='https://www.strava.com/api/v3/activities',
                             data={'name': a_name,
                                   'type': a_type,
                                   'start_date_local': a_time,
                                   'elapsed_time': a_ellapsed,
                                   'description': a_description,
                                   'code': api_token,
                                   'grant_type': 'authorization_code'
                                   },
                             headers = {'Authorization': f'Bearer {api_token}'}
                             )
    print(response.text)

if __name__ == "__main__":
    main()
