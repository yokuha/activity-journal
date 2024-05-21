#!/usr/bin/env python
#
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

import json
import mdutils
from mdutils.mdutils import MdUtils
import re
from settings import athlete_id

# load athlete and activities info
activities_file = f'{athlete_id}-activities.json'
athlete_file = f'{athlete_id}-athlete.json'
with open(athlete_file, 'r', encoding='utf-8') as db:
    athlete = json.load(db)
with open(activities_file, 'r', encoding='utf-8') as db:
    activities = json.load(db)


def get(data, entry):
    try:
        if str != type(data[entry]):
            return str(int(data[entry]))
        return data[entry]
    except:
        if entry in ['AP', 'NP', 'calories']:
            return '—'
        return ''


# create markdown text from info in the current athletes files
mdFile = MdUtils(file_name=f'{athlete_id}.md', title=f'Activity journal of athlete {athlete_id} ({athlete["username"]})')
mdFile.new_header(level=1, title=f'Athlete info: {athlete["firstname"]} {athlete["lastname"]}')
mdFile.new_paragraph(f'``https://www.strava.com/athletes/{athlete_id}``\n')
mdFile.new_paragraph(athlete["bio"].replace('\n', '    \n'))

# and print info on the athletes activities
mdFile.new_header(level=1, title='Activities')
for id in sorted(activities, reverse=True):
    data = activities[id]
    # print activity title (date)
    if 'date' in data and None != data['date'] and len(data['date']) > 0:
        mdFile.new_header(level=2, title=f'{data["name"]} ({data["date"].replace("T", " ").replace("Z", " h")})')
    else:
        mdFile.new_header(level=2, title=data['name'])
    # print URL on Strava
    mdFile.new_paragraph(f'``https://www.strava.com/activities/{id}``\n')
    # print some basic data of activity
    mdFile.new_paragraph(f'AP = {get(data, "AP")} W, NP = {get(data, "NP")} W, calories = {get(data, "calories")} kcal\n')
    # print public and private notes
    public_note = ''
    if 'note' in data and None != data['note'] and len(data['note']) > 0:
        public_note = re.sub(r'-- myWindsock Report.*END --', '', data['note'], flags=re.DOTALL).replace('\r', '   ')
    private_note = ''
    if 'private_note' in data and None != data['private_note'] and len(data['private_note']) > 0:
        private_note = data['private_note'].replace('\r', '   ')
    # via html table
    mdFile.new_paragraph(f'{private_note}\n{public_note}\n')

# save markdown file
mdFile.create_md_file()

print('activity journal updated, creating PDF')

# create updated PDF
import subprocess
subprocess.call(['pandoc', '-d', 'pandoc.yaml', '-o', f'{athlete_id}.pdf', f'{athlete_id}.md'])



### Local Variables:
### coding: utf-8
### truncate-lines: t
### End:
