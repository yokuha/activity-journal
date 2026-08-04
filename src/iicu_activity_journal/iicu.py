# activity-journal -- create a journal of the notes of your own intervals.icu activities.
# Copyright (C) 2023,2024 yokuha <jokuha@icloud.com>
#
# intervals.icu authorization and functionality
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


import base64
import os
import shlex
import subprocess
from pathlib import Path


def load_credentials():
    """Read the athlete ID and API key from an encrypted authinfo file."""
    authinfo_file = Path(
        os.environ.get('IICU_AUTHINFO_FILE', '~/.authinfo.gpg')
    ).expanduser()
    try:
        result = subprocess.run(
            ['gpg', '--quiet', '--decrypt', str(authinfo_file)],
            capture_output=True,
            check=True,
            encoding='utf-8',
        )
    except FileNotFoundError as err:
        raise RuntimeError(
            'The gpg executable is required to read credentials.'
        ) from err
    except subprocess.CalledProcessError as err:
        raise RuntimeError(f'Could not decrypt {authinfo_file}.') from err

    for line in result.stdout.splitlines():
        fields = shlex.split(line, comments=True)
        if len(fields) < 2 or fields[0] != 'machine':
            continue
        entry = dict(zip(fields[::2], fields[1::2]))
        if entry.get('machine') == 'intervals.icu':
            try:
                return entry['login'], entry['password']
            except KeyError as err:
                raise RuntimeError(
                    'The intervals.icu authinfo entry needs login and password.'
                ) from err

    raise RuntimeError(
        f'No intervals.icu machine entry found in {authinfo_file}.'
    )


athlete_id, api_key = load_credentials()

# API_KEY for basic authentication
auth_key = b'Basic ' + base64.b64encode(f'API_KEY:{api_key}'.encode('ascii'))

# Filenames for local storage of activity data
logbook_basename = f'logbook-{athlete_id}'
activities_file = logbook_basename + '-activity-data.json'
athlete_file = logbook_basename + '-athlete-info.json'

# activity items to store locally and their logbook output names
item_names = {'type': 'type',
              'name': 'name',
              'commute': 'commute',
              'date': 'start_date_local',
              'end_date': 'end_date_local',
              'duration': 'elapsed_time',
              'note': 'description',
              'AP': 'icu_average_watts',
              'FTP': 'icu_ftp',
              'IF': 'icu_intensity',
              'L/R': 'avg_lr_balance',
              'load': 'icu_training_load_data',
              'RPE': 'icu_rpe',
              'calories': 'calories',
              'category': 'category',
              'notes': 'messages',
              'attachments': 'attachments',
              }




### Local Variables:
### coding: utf-8
### truncate-lines: t
### End:
