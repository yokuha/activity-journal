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

"""Find the intervals.icu athlete ID and API key.

Sources, in order of precedence:

1. the environment variables ``INTERVALS_ICU_ATHLETE_ID`` and
   ``INTERVALS_ICU_API_KEY``,
2. a ``.env`` file: the one given explicitly, otherwise ``<env_dir>/.env``
   (the CLI passes the current directory),
3. an intervals.icu entry in an encrypted authinfo file (``~/.authinfo.gpg``,
   or ``IICU_AUTHINFO_FILE``), decrypted with ``gpg`` only if needed.

The key is never printed or stored by this module.
"""

import os
import shlex
import subprocess
from dataclasses import dataclass
from pathlib import Path

ENV_API_KEY = 'INTERVALS_ICU_API_KEY'
ENV_ATHLETE_ID = 'INTERVALS_ICU_ATHLETE_ID'


class CredentialsError(RuntimeError):
    """Raised when no usable credentials can be found."""


@dataclass(frozen=True)
class Credentials:
    athlete_id: str
    api_key: str = ''

    def __repr__(self):
        # Keep the key out of tracebacks and logs.
        return f'Credentials(athlete_id={self.athlete_id!r}, api_key=<hidden>)'


def parse_env_file(path):
    """Read KEY=VALUE lines (optional ``export``, optional quotes)."""
    values = {}
    for line in Path(path).read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        if line.startswith('export '):
            line = line[len('export '):]
        key, value = line.split('=', 1)
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in '"\'':
            value = value[1:-1]
        values[key.strip()] = value
    return values


def parse_authinfo(text):
    """Return ``(login, password)`` of the intervals.icu entry, or ``None``."""
    for line in text.splitlines():
        fields = shlex.split(line, comments=True)
        if len(fields) < 2 or fields[0] != 'machine':
            continue
        entry = dict(zip(fields[::2], fields[1::2], strict=False))
        if entry.get('machine') == 'intervals.icu':
            try:
                return entry['login'], entry['password']
            except KeyError as err:
                raise CredentialsError(
                    'The intervals.icu authinfo entry needs login and password.'
                ) from err
    return None


def _from_authinfo():
    authinfo_file = Path(
        os.environ.get('IICU_AUTHINFO_FILE', '~/.authinfo.gpg')
    ).expanduser()
    if not authinfo_file.is_file():
        return None
    try:
        result = subprocess.run(
            ['gpg', '--quiet', '--decrypt', str(authinfo_file)],
            capture_output=True, check=True, encoding='utf-8',
        )
    except FileNotFoundError as err:
        raise CredentialsError(
            'The gpg executable is required to read credentials.'
        ) from err
    except subprocess.CalledProcessError as err:
        raise CredentialsError(f'Could not decrypt {authinfo_file}.') from err
    return parse_authinfo(result.stdout)


def load_credentials(env_file=None, env_dir=None):
    """Find the credentials; raise ``CredentialsError`` if there are none."""
    api_key = os.environ.get(ENV_API_KEY) or ''
    athlete_id = os.environ.get(ENV_ATHLETE_ID) or ''

    if not (api_key and athlete_id):
        if env_file:
            candidate = Path(env_file).expanduser()
            if not candidate.is_file():
                raise CredentialsError(f'Env file {candidate} does not exist.')
        elif env_dir:
            candidate = Path(env_dir) / '.env'
        else:
            candidate = None
        if candidate is not None and candidate.is_file():
            values = parse_env_file(candidate)
            api_key = api_key or values.get(ENV_API_KEY, '')
            athlete_id = athlete_id or values.get(ENV_ATHLETE_ID, '')

    if not (api_key and athlete_id):
        entry = _from_authinfo()
        if entry:
            athlete_id = athlete_id or entry[0]
            api_key = api_key or entry[1]

    if not api_key:
        raise CredentialsError(
            f'No API key found. Set {ENV_API_KEY} and {ENV_ATHLETE_ID}, '
            'provide a .env file (--env), or add an intervals.icu entry to '
            'your encrypted authinfo file.'
        )
    if not athlete_id:
        raise CredentialsError(f'No athlete ID found; set {ENV_ATHLETE_ID}.')
    return Credentials(athlete_id=athlete_id, api_key=api_key)
