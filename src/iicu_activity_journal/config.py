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

"""Optional personal settings for the journal (a TOML file).

Example ``journal.toml``::

    author = "Your Name"
    show_email = false

    [name_aliases]
    your-intervals-username = "JK"
"""

import sys
from dataclasses import dataclass, field
from pathlib import Path

if sys.version_info >= (3, 11):
    import tomllib
else:  # pragma: no cover
    import tomli as tomllib


@dataclass
class JournalConfig:
    author: str = ''
    show_email: bool = False
    name_aliases: dict[str, str] = field(default_factory=dict)

    def display_name(self, name):
        return self.name_aliases.get(name, name)


def load_config(path):
    """Read a config file; a missing file means defaults."""
    if path is None or not Path(path).is_file():
        return JournalConfig()
    with open(path, 'rb') as fh:
        data = tomllib.load(fh)
    aliases = data.get('name_aliases', {})
    if not isinstance(aliases, dict):
        raise ValueError('name_aliases must be a table of name = "alias" pairs.')
    return JournalConfig(
        author=str(data.get('author', '')),
        show_email=bool(data.get('show_email', False)),
        name_aliases={str(k): str(v) for k, v in aliases.items()},
    )
