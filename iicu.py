# intervals.icu authorization and functionality functions
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


import base64
from settings import *

# API_KEY for basic authentication
auth_key = b'Basic ' + base64.b64encode(f'API_KEY:{api_key}'.encode('ascii'))

# Filename for local storage of activity data
activities_file = f'logbook-{athlete_id}-activity-data.json'

# activity items to store locally and their logbook output names
item_names = {'name': 'name',
              'date': 'start_date',
              'note': 'description',
              'AP': 'icu_average_watts',
              'calories': 'calories',
              'L/R': 'avg_lr_balance'
              }




### Local Variables:
### coding: utf-8
### truncate-lines: t
### End:
