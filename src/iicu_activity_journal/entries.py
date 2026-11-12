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

"""Journal entries (activities and calendar notes) read from the archive."""

import gzip
import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

# Calendar events that belong in the journal.
EVENT_CATEGORIES = ('HOLIDAY', 'INJURED', 'SICK', 'NOTE', 'RACE_A', 'RACE_B', 'RACE_C')


@dataclass
class Message:
    name: str
    content: str
    attachment_url: str = ''


@dataclass
class Entry:
    id: str
    kind: str  # 'activity' or 'event'
    start: datetime
    name: str = ''
    type: str = ''
    category: str = ''
    commute: bool = False
    end: datetime | None = None
    duration: float | None = None  # seconds
    note: str = ''
    avg_power: float | None = None
    ftp: float | None = None
    intensity: float | None = None  # percent of FTP
    lr_balance: float | None = None  # percent right
    rpe: float | None = None
    calories: float | None = None
    messages: list[Message] = field(default_factory=list)

    @property
    def incomplete(self):
        """Restricted or imported-elsewhere activities come without a name."""
        return not self.name

    @property
    def link(self):
        """intervals.icu URL; only native ``i...`` activities have one."""
        if self.kind == 'activity' and self.id.startswith('i'):
            return f'https://intervals.icu/activities/{self.id}'
        return None


@dataclass
class Archive:
    athlete: dict
    entries: list[Entry]
    skipped: int = 0


def _read_json(path):
    with gzip.open(path, 'rt', encoding='utf-8') as fh:
        return json.load(fh)


def _parse(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value).replace(tzinfo=None)
    except ValueError:
        return None


def _messages(directory, entry_id):
    path = directory / f'{entry_id}.json.gz'
    if not path.is_file():
        return []
    result = []
    for raw in _read_json(path):
        if raw.get('deleted'):
            continue
        content = raw.get('content') or ''
        url = raw.get('attachment_url') or ''
        if content or url:
            result.append(Message(raw.get('name') or '', content, url))
    return result


def _activity(raw, directory):
    start = _parse(raw.get('start_date_local'))
    if start is None:
        return None
    return Entry(
        id=str(raw['id']), kind='activity', start=start,
        name=raw.get('name') or '', type=raw.get('type') or '',
        commute=bool(raw.get('commute')),
        duration=raw.get('elapsed_time'), note=raw.get('description') or '',
        avg_power=raw.get('icu_average_watts'), ftp=raw.get('icu_ftp'),
        intensity=raw.get('icu_intensity'), lr_balance=raw.get('avg_lr_balance'),
        rpe=raw.get('icu_rpe'), calories=raw.get('calories'),
        messages=_messages(directory, raw['id']),
    )


def _event(raw):
    start = _parse(raw.get('start_date_local'))
    if start is None:
        return None
    return Entry(
        id=str(raw['id']), kind='event', start=start,
        name=raw.get('name') or '', type=raw.get('type') or '',
        category=raw['category'], end=_parse(raw.get('end_date_local')),
        note=raw.get('description') or '',
    )


def load_archive(archive_dir):
    """Read the archive written by ``iicu-journal archive``."""
    archive_dir = Path(archive_dir)
    activities_path = archive_dir / 'activities.json.gz'
    if not activities_path.is_file():
        raise FileNotFoundError(
            f'{activities_path} not found; run "iicu-journal archive all" first.')

    athlete = {}
    if (archive_dir / 'athlete.json.gz').is_file():
        profile = _read_json(archive_dir / 'athlete.json.gz')
        athlete = profile.get('athlete', profile)

    entries, skipped = [], 0
    for raw in _read_json(activities_path):
        entry = _activity(raw, archive_dir / 'activity-messages')
        if entry is None:
            skipped += 1
        else:
            entries.append(entry)
    events_path = archive_dir / 'events.json.gz'
    if events_path.is_file():
        for raw in _read_json(events_path):
            if raw.get('category') not in EVENT_CATEGORIES:
                continue
            entry = _event(raw)
            if entry is None:
                skipped += 1
            else:
                entries.append(entry)
    entries.sort(key=lambda e: (e.start, e.id), reverse=True)
    return Archive(athlete=athlete, entries=entries, skipped=skipped)
