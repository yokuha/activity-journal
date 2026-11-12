# activity-journal -- create a journal of the notes of your own intervals.icu activities.
# Copyright (C) 2023-2026 yokuha <jokuha@icloud.com>
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

"""Plot the left/right balance of an activity against power."""

from pathlib import Path


def balance_histogram(power, lrb):
    """Smoothed 2D histogram of power and right-leg fraction.

    Returns ``(x centers, y centers, H)`` with ``H`` normalized to a peak of 100.
    """
    import numpy as np
    from scipy.ndimage import gaussian_filter

    xedges = np.arange(0, np.max(power) + 11, 10)
    yedges = np.arange(30, 71, 1)
    hist, xedges, yedges = np.histogram2d(power, lrb, bins=(xedges, yedges))
    hist = gaussian_filter(hist.T, 0.75)
    hist *= 100 / hist.max()
    return (xedges[:-1] + xedges[1:]) / 2, (yedges[:-1] + yedges[1:]) / 2, hist


def plot_balance(client, activity_id, output, show=False):
    import matplotlib.pyplot as plt
    import numpy as np

    streams = {s['type']: s['data'] for s in client.get_json(
        f'activity/{activity_id}/streams', types='watts,left_right_balance')}
    if 'watts' not in streams or 'left_right_balance' not in streams:
        raise RuntimeError(f'Activity {activity_id} has no power/balance streams.')
    power = np.array([v or 0 for v in streams['watts']], dtype=int)
    lrb = np.array([np.nan if v is None else v for v in streams['left_right_balance']],
                   dtype=float)
    xcenters, ycenters, hist = balance_histogram(power, lrb)

    levels = np.arange(0., 105, 10)
    plt.contourf(xcenters, ycenters, hist, levels=levels, cmap='Reds', antialiased=True)
    plt.xlabel('power (W)')
    plt.ylabel('R fraction of L-R balance (%)')
    plt.colorbar(label='rel. contribution (% of peak)')
    plt.savefig(Path(output))
    if show:
        plt.show()
    plt.close()
