#!/usr/bin/env python
#
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
from settings import *

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
