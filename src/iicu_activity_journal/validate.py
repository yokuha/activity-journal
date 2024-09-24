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

# based on https://gist.github.com/htv2012/ad8c19ac43e128aa7ee1


"""Check/validate json data for activities for activity journal"""


import json

import click
import collections
import requests

from iicu_activity_journal import iicu
from iicu_activity_journal.iicu import activities_file


def detect_duplicate_keys(list_of_pairs):
    key_count = collections.Counter(k for k,v in list_of_pairs)
    duplicate_keys = ', '.join(k for k,v in key_count.items() if v>1)

    if len(duplicate_keys) != 0:
        raise ValueError('Duplicate key(s) found: {}'.format(duplicate_keys))


def validate_data(list_of_pairs):
    detect_duplicate_keys(list_of_pairs)
    # more dectection, each of them should raise an exception upon invalid data
    return dict(list_of_pairs)


def main():
    with open(activities_file, 'r', encoding='utf-8') as db:
        activities = json.load(db, object_pairs_hook=validate_data)
    print(activities)



if __name__ == "__main__":
    main()
