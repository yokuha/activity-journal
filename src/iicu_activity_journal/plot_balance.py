#!/usr/bin/env python
#
# activity-journal -- create a journal of the notes of your own intervals.icu activities.
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

import click
import json
import numpy as np
from pathlib import Path
import requests
from scipy.ndimage import gaussian_filter

from matplotlib.image import NonUniformImage
import matplotlib.pyplot as plt

from iicu import *


@click.command()
@click.help_option('--help', '-h')
@click.option('-a', '--activity', 'a_activity_id', default=None, required=True,
              help='i.icu activity ID')
def main(a_activity_id):
    # Get the activity's L-R-balance data
    response = requests.get(url = f'https://intervals.icu/api/v1/activity/{a_activity_id}/streams?types=watts,left_right_balance',
                            headers = {'Authorization': auth_key})
    # extract data
    data = json.loads(response.text)
    power = np.array(data[0]['data'], dtype=int)
    for i in range(len(data[1]['data'])): # fix 'None' values in data
        if int != type(data[1]['data'][i]): data[1]['data'][i] = np.NaN
    lrb =  np.array(data[1]['data'])

    # create histogram
    xedges = np.arange(0,np.max(power)+11,10)
    yedges = np.arange(30,71,1)
    xcenters = (xedges[:-1] + xedges[1:]) / 2
    ycenters = (yedges[:-1] + yedges[1:]) / 2
    H, xedges, yedges = np.histogram2d(power, lrb, bins=(xedges, yedges))
    # Histogram does not follow Cartesian convention, therefore, transpose H for visualization purposes.
    H = H.T
    # smooth data
    H = gaussian_filter(H, 0.75)
    # normalize to peak 100
    H *= 100 / H.max()

    # plot data
    levels = np.arange(0., 105, 10)
    cs = plt.contourf(xcenters, ycenters, H, levels=levels, cmap='Reds', antialiased=True)
    # proxy = [plt.Rectangle((0, 0), 1, 1, fc=fc) for fc in cs.get_facecolors()]
    # plt.legend(proxy, [f'{lower:2.0f}--{upper:2.0f} \\%' for lower, upper in zip(levels[:-1]*100, levels[1:]*100)])
    plt.xlabel('power (W)')
    plt.ylabel('R fraction of L-R balance (\\%)')
    plt.colorbar(label='rel. contribution (\\% of peak)')
    plt.savefig(Path.home() / 'Downloads' / f'{a_activity_id}.png')
    plt.show()


if __name__ == "__main__":
    main()
