#!/usr/bin/env python
#
# activity-journal -- create a journal of the notes of your intervals.icu activities.
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

import json
import mdutils
from mdutils.mdutils import MdUtils
import re

from iicu import *

# load athlete and activities info
with open(athlete_file, 'r', encoding='utf-8') as db:
    athlete = json.load(db)["athlete"]
with open(activities_file, 'r', encoding='utf-8') as db:
    activities = json.load(db)


def get(data, entry):
    try:
        if 'NP' == entry:
            return str(int(int(data['FTP'])*float(data['IF']/100)))
        if 'L/R' == entry:
            r = data[entry]
            return(f'{int(100-r)}/{int(r)}')
        else:
            if str != type(data[entry]):
                return str(int(data[entry]))
            return data[entry]
    except:
        if entry in ['AP', 'NP', 'IF', 'FTP', 'L/R', 'calories']:
            return '—'
        return ''


# create markdown text from info in the current athletes files
mdf = MdUtils(file_name=f'{logbook_basename}.md',
              title=f'Activity journal of athlete {athlete["name"]} (id: {athlete_id})',
              author = 'activity-journal package by yokuha')
# mdf.new_header(level=1, title=f'Athlete info: {athlete["firstname"]} {athlete["lastname"]}')
mdf.new_paragraph(f'``https://intervals.icu/athlete/{athlete_id}/fitness``\n')
if athlete["email"]: mdf.new_paragraph(athlete["email"])
mdf.new_paragraph(athlete["bio"].replace('\n', '    \n'))

mdf.new_paragraph('---')

# and print info on the athletes activities
mdf.new_header(level=1, title='Activities')
for id in sorted(activities, reverse=True):
    data = activities[id]
    # print activity title (date)
    if 'date' in data and None != data['date'] and len(data['date']) > 0:
        mdf.new_header(level=2, title=f'{data["name"]} ({data["date"].replace("T", " ").replace("Z", " h")})')
    else:
        mdf.new_header(level=2, title=data['name'])
    # print URL on Strava
    mdf.new_paragraph(f'``https://intervals.icu/activities/{id}``\n')
    # print some basic data of activity
    if 'Ride' in get(data, 'type'):
        mdf.new_paragraph(f'AP = {get(data, "AP")} W, '
                          f'NP = {get(data, "NP")} W, '
                          f'IF = 0.{get(data, "IF")} (FTP = {get(data, "FTP")}), '
                          f'L/R = {get(data, "L/R")}, '
                          f'calories = {get(data, "calories")} kcal\n')
    else:
        mdf.new_paragraph(f'IF = 0.{get(data, "IF")}, '
                          f'calories = {get(data, "calories")} kcal\n')

    # print public and private notes
    public_note = ''
    if 'note' in data and None != data['note'] and len(data['note']) > 0:
        public_note = re.sub(r'-- myWindsock.com Report.*END --', '', data['note'], flags=re.DOTALL).replace('\r', '   ')
    private_note = ''
    if 'private_note' in data and None != data['private_note'] and len(data['private_note']) > 0:
        private_note = data['private_note'].replace('\r', '   ')
    if len(public_note) + len(private_note) > 0:
        mdf.new_header(level=3, title='Description')
        mdf.new_paragraph(f'{private_note}\n{public_note}\n')


# save markdown file
mdf.create_md_file()

print('activity journal updated, creating PDF')

# create updated PDF
import subprocess
subprocess.call(['pandoc', '-d', 'pandoc.yaml', '-o', f'{logbook_basename}.pdf', f'{logbook_basename}.md'])



### Local Variables:
### coding: utf-8
### truncate-lines: t
### End:
