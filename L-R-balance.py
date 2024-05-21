#!/usr/bin/env python
#
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
import click
import json
import numpy as np
import requests
from settings import *

from matplotlib.image import NonUniformImage
import matplotlib.pyplot as plt


@click.command()
@click.help_option('--help', '-h')
@click.option('-a', '--activity', 'a_activity_id', default=None, required=True,
              help='i.icu activity ID')
def main(a_activity_id):
    api_key = b'Basic ' + base64.b64encode(f'API_KEY:{intervals_api_key}'.encode('ascii'))
    # Get the Activity
    # response = requests.get(url = f'https://intervals.icu/api/v1/athlete/{intervals_athlete_id}/activities/{a_activity_id}',
    #                         headers = {'Authorization': api_key}
    #                         )
    # get activity's L-R-balance data
    response = requests.get(url = f'https://intervals.icu/api/v1/activity/{a_activity_id}/streams?types=watts,left_right_balance',
                            headers = {'Authorization': api_key}
                            )
    #print(response.json())
    data = json.loads(response.text)
    power = np.array(data[0]['data'], dtype=int)
    lrb =  np.array(data[1]['data'], dtype=int)

    xedges = np.arange(0,np.max(power)+11,10)
    yedges = np.arange(30,71,1)
    H, xedges, yedges = np.histogram2d(power, lrb, bins=(xedges, yedges))


if __name__ == "__main__":
    main()
