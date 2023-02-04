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
from settings import athlete_id

# load athlete and activities info
activities_file = f'{athlete_id}-activities.json'
athlete_file = f'{athlete_id}-athlete.json'
with open(athlete_file, 'r', encoding='utf-8') as db:
    athlete = json.load(db)
with open(activities_file, 'r', encoding='utf-8') as db:
    activities = json.load(db)


# create mardown text of all info in the current athletes files
mdFile = MdUtils(file_name=f'{athlete_id}.md', title=f'Activity journal of athlete {athlete_id} ({athlete["username"]})')
mdFile.new_header(level=1, title='Athlete info')
mdFile.new_paragraph(f'{athlete["firstname"]} {athlete["lastname"]}')
mdFile.new_paragraph(athlete["bio"].replace('\n', '    \n'))
mdFile.new_paragraph('\clearpage\n\n')

mdFile.new_header(level=1, title='Activities')
for id in sorted(activities, reverse=True):
    data = activities[id]
    # print activity title (date)
    if 'date' in data and None != data['date'] and len(data['date']) > 0:
        mdFile.new_header(level=2, title=f'{data["name"]} ({data["date"].replace("T", " ").replace("Z", " h")})')
    else:
        mdFile.new_header(level=2, title=data['name'])
    # print URL on Strava
    mdFile.new_paragraph(f'``https://www.strava.com/activities/{id})``')
    # print notes
    anynote = False
    if 'note' in data and None != data['note'] and len(data['note']) > 0:
        mdFile.new_paragraph(data['note'].replace('\r', '   '))
        mdFile.new_paragraph('---\n')
        anynote = True
    if 'private_note' in data and None != data['private_note'] and len(data['private_note']) > 0:
        mdFile.new_paragraph()
        mdFile.new_header(level=3, title='Private notes')
        mdFile.new_paragraph(data['private_note'].replace('\r', '   '))
        mdFile.new_paragraph('---\n')
        anynote = True
    if not anynote:
        mdFile.new_paragraph('\n')
        mdFile.new_paragraph('---\n')
mdFile.create_md_file()
