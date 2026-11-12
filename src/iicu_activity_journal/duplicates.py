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

"""Find potential duplicate activities."""

from datetime import timedelta
from itertools import pairwise


def find_duplicates(entries, *, start_gap=timedelta(minutes=15),
                    duration_gap=timedelta(minutes=15)):
    """Pairs of neighboring activities that start close together and last
    about equally long."""
    activities = sorted((e for e in entries if e.kind == 'activity'),
                        key=lambda e: e.start)
    pairs = []
    for first, second in pairwise(activities):
        if second.start - first.start > start_gap:
            continue
        if None not in (first.duration, second.duration):
            difference = abs(first.duration - second.duration)
            if difference > duration_gap.total_seconds():
                continue
        pairs.append((first, second))
    return pairs
