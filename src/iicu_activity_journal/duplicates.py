#!/usr/bin/env python
#
# activity-journal -- create a journal of the notes of your own intervals.icu activities.
# Copyright (C) 2023,2024,2025 yokuha <jokuha@icloud.com>
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


"""Find duplicates in local database

Searches local database for activities that have starttimes within 15 min and
durations that do not differ by more than 15 min.

"""


import json
import re

import click
import datetime as dt
from itertools import pairwise

from iicu_activity_journal.iicu import activities_file, athlete_file, athlete_id, logbook_basename
from iicu_activity_journal import validate



@click.command()
@click.help_option('--help', '-h')
@click.option('-b', '--begin', 'a_begin', default=dt.datetime.min, required=False, show_default=True,
              help='Beginning of date range for search')
@click.option('-e', '--end', 'a_end', default=dt.datetime.max, required=False, show_default=True,
              help='End of date range for search')
@click.option('-c', '--commute', 'a_commute', is_flag=True, default=False, show_default=True,
              help='Include commutes in search')
def main(a_begin, a_end, a_commute):
    """Search for duplicates"""

    # load activities info
    with open(activities_file, 'r', encoding='utf-8') as db:
        activities = json.load(db, object_pairs_hook=validate.validate_data)

    # iterate activities pairwise and check if they are identical
    count = 0
    for a_id, b_id in pairwise(dict(sorted(activities.items(),
                          key=lambda item: dt.datetime.fromisoformat(item[1]['date']),
                          reverse=True))):
        a = activities[a_id]
        b = activities[b_id]
        if ('date' in a and None != a['date'] and len(a['date']) > 0) and ('date' in b and None != b['date'] and len(b['date']) > 0):
            if dt.datetime.fromisoformat(a['date']).date() - dt.datetime.fromisoformat(b['date']).date() < dt.timedelta(minutes=15):
                if dt.datetime.fromisoformat(a['date']).date() - dt.datetime.fromisoformat(b['date']).date() < dt.timedelta(minutes=5):
                    count += 1
                    print('\n\nPotential duplicates:')
                    for id in[a_id, b_id]:
                        if 'i' == id[0]:
                            print(f'https://intervals.icu/activities/{id}')
                        else:
                            print(f'No i.icu link available for {id}; feature is requested upstream.')
    print(f'\n\nFound {count} duplicates')



if __name__ == "__main__":
    main()



### Local Variables:
### coding: utf-8
### truncate-lines: t
### End:
