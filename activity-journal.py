#!/usr/bin/env python
#
# Approach for accessing Strava data based on https://www.grace-dev.com/python-apis/strava-api
# Copyright (C) 2022 yokuha
import json
import mdutils
from mdutils.mdutils import MdUtils
import sys


athlete_id = sys.argv[1]

# load athlete and activities info
info_file = f'{athlete_id}-info.json'
athlete_file = f'{athlete_id}-athlete.json'
with open(athlete_file, 'r', encoding='utf-8') as db:
    athlete = json.load(db)
with open(info_file, 'r', encoding='utf-8') as db:
    info = json.load(db)


# create mardown text of all info in the current athlestes files
mdFile = MdUtils(file_name=f'{athlete_id}.md', title=f'Activity journal of athlete {athlete_id} ({athlete["username"]})')
mdFile.new_header(level=1, title='Athlete info')
mdFile.new_header(level=2, title='Activities')
for id in info.keys():
    data = info[id]
    mdFile.new_paragraph()
    mdFile.new_header(level=3, title=data['name'])
    anynote = False
    if 'note' in data and None != data['note'] and len(data['note']) > 0:
        mdFile.new_paragraph(data['note'].replace('\r', '   '))
        mdFile.new_paragraph('---')
        anynote = True
    if 'private_note' in data and None != data['private_note'] and len(data['private_note']) > 0:
        mdFile.new_paragraph()
        mdFile.new_header(level=4, title='Private notes')
        mdFile.new_paragraph(data['private_note'].replace('\r', '   '))
        mdFile.new_paragraph('---')
        anynote = True
    if not anynote:
        mdFile.new_paragraph('\ ')
        mdFile.new_paragraph('---')
mdFile.create_md_file()
