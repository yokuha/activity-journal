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


# Template with settings
# copy these definitions to a file `settings'py` and fill it with your own information.

# settings for authentication and accessing Strava's API
# see https://www.strava.com/settings/api for the corresponding data
client_id = '...'
client_secret = '...'
redirect_uri = 'http://localhost/'

# athlete_id
athlete_id = '...'

# date (week) range for which to fetch data
fetch_weeks = range(0,-1,-1) # default is to fetch data only for the last/current week (last 7 days)


intervals_athlete_id = '...'
intervals_api_key = '...'



### Local Variables:
### coding: utf-8
### truncate-lines: t
### End:
