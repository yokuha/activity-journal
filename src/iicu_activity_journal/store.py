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

"""Reproducible local storage for backed-up data.

All JSON is written gzip-compressed (level 9, no timestamp, no file name in
the header) with sorted keys. Identical content therefore yields byte-identical
files, so git (also with git-crypt) does not store unchanged files again.
"""

import gzip
import json
import os
from pathlib import Path


def _write_bytes(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_file() and path.read_bytes() == data:
        return False
    tmp = path.with_name(path.name + '.tmp')
    tmp.write_bytes(data)
    os.replace(tmp, path)
    return True


def write_gz(path, data):
    """Write ``data`` (bytes) reproducibly gzip-compressed."""
    return _write_bytes(path, gzip.compress(data, compresslevel=9, mtime=0))


def write_json_gz(path, obj):
    text = json.dumps(obj, indent=1, sort_keys=True, ensure_ascii=False) + '\n'
    return write_gz(path, text.encode('utf-8'))


def read_json_gz(path):
    with gzip.open(path, 'rt', encoding='utf-8') as fh:
        return json.load(fh)


def append_logbook(readme, line):
    """Append a line to the ``# logbook`` section of a README.md."""
    readme = Path(readme)
    text = readme.read_text(encoding='utf-8') if readme.is_file() else ''
    if '# logbook' not in text:
        text = text.rstrip('\n') + '\n\n---\n\n# logbook\n'
    readme.write_text(text.rstrip('\n') + '\n\n' + line + '\n', encoding='utf-8')
