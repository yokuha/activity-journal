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
import settings

api_key = b'Basic ' + base64.b64encode(f'API_KEY:{settings.api_key}'.encode('ascii'))


# # Strava info translation to local json file
# translation = {'name': 'name',
#                'date': 'start_date',
#                'note': 'description',
#                'private_note': 'private_note',
#                'AP': 'average_watts',
#                'NP': 'weighted_average_watts',
#                'calories': 'calories'
#                }



# def store(name, strava, local):
#     """Store value locally"""
#     if translation[name] in strava and len(str(strava[translation[name]])) > 0:
#         local.update({name: strava[translation[name]]})





### Local Variables:
### coding: utf-8
### truncate-lines: t
### End:
