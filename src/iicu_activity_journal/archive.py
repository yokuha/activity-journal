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

"""Archive intervals.icu data to a local directory.

Layout of the archive directory::

    athlete.json.gz                 profile
    sport-settings.json.gz          per-sport settings
    gear.json.gz                    gear list (distance, time, components, ...)
    activities.json.gz              all activities (metadata), sorted by date
    activities.csv.gz               CSV export of the activities
    activity-details/<id>.json.gz   details per activity incl. intervals
    activity-messages/<id>.json.gz  notes/messages per activity
    events.json.gz                  calendar events (notes, races, holidays, ...)
    wellness.json.gz                all wellness records
    wellness backup – HRV + Baevsky.csv   rMSSD, SDNN and Baevsky SI

FIT/GPX files and per-second streams are not part of this archive.
"""

import csv
import time
from datetime import date, timedelta
from pathlib import Path

from iicu_activity_journal.api import ApiError
from iicu_activity_journal.store import read_json_gz, write_gz, write_json_gz

ACTIVITY_CHUNK_DAYS = 365
ACTIVITY_LIMIT = 2000
EVENT_CHUNK_DAYS = 365
WELLNESS_CHUNK_DAYS = 180
DEFAULT_START = date(2015, 1, 1)
HRV_CSV_NAME = 'wellness backup – HRV + Baevsky.csv'


def date_chunks(start, end, days):
    """Yield consecutive ``(first, last)`` date pairs of at most ``days`` days."""
    current = start
    while current <= end:
        last = min(current + timedelta(days=days - 1), end)
        yield current, last
        current = last + timedelta(days=1)


def _plus_one(day):
    # The API treats ``newest`` as exclusive for some endpoints; ask for one
    # extra day so the last day is included. Duplicates are removed by id.
    return day + timedelta(days=1)


def _no_echo(_message):
    pass


def merge_records(path, fetched, start, end, key, day):
    """Combine ``fetched`` records with those already saved at ``path``.

    Saved records inside ``start``..``end`` are dropped (the server is
    authoritative for that range), everything outside is kept, so a run for a
    short period never shrinks the archive. ``key(record)`` is the unique id,
    ``day(record)`` the ISO date of the record.
    """
    merged = {}
    if Path(path).is_file():
        for record in read_json_gz(path):
            if not start.isoformat() <= (day(record) or '')[:10] <= end.isoformat():
                merged[key(record)] = record
    for record in fetched:
        merged[key(record)] = record
    return list(merged.values())


def _start_day(record):
    return record.get('start_date_local') or ''


def archive_athlete(client, out, echo=_no_echo):
    write_json_gz(out / 'athlete.json.gz',
                  client.get_json(client.athlete_path('profile')))
    write_json_gz(out / 'sport-settings.json.gz',
                  client.get_json(client.athlete_path('sport-settings')))
    echo('Athlete profile and sport settings saved.')
    return 'athlete profile and sport settings'


def archive_gear(client, out, echo=_no_echo):
    gear = client.get_json(client.athlete_path('gear'))
    gear = sorted(gear, key=lambda g: (str(g.get('name') or ''), str(g.get('id'))))
    write_json_gz(out / 'gear.json.gz', gear)
    echo(f'{len(gear)} gear items saved.')
    return f'{len(gear)} gear items'


def list_activities(client, start, end, echo=_no_echo):
    found = {}
    for first, last in date_chunks(start, end, ACTIVITY_CHUNK_DAYS):
        data = client.get_json(client.athlete_path('activities'),
                               oldest=first, newest=_plus_one(last),
                               limit=ACTIVITY_LIMIT)
        if len(data) >= ACTIVITY_LIMIT:
            echo(f'Warning: {first}..{last} returned {len(data)} activities; '
                 'the list may be truncated.')
        for activity in data:
            if activity.get('id'):
                found[str(activity['id'])] = activity
    return sorted(found.values(),
                  key=lambda a: (a.get('start_date_local') or '', str(a['id'])))


def load_activities(out):
    """Activity list of an earlier ``archive activities`` run."""
    path = out / 'activities.json.gz'
    if not path.is_file():
        raise FileNotFoundError(
            f'{path} not found; run "archive activities" first.')
    return read_json_gz(path)


def archive_activities(client, out, start, end, echo=_no_echo):
    """Save the list of activities (JSON and CSV); return the fetched ones.

    The saved list is extended: only the requested range is replaced. The CSV
    export is not mergeable and is therefore only written for a run that
    starts at the default start date or earlier.
    """
    activities = list_activities(client, start, end, echo)
    path = out / 'activities.json.gz'
    merged = merge_records(path, activities, start, end,
                           key=lambda a: str(a['id']), day=_start_day)
    merged.sort(key=lambda a: (_start_day(a), str(a['id'])))
    write_json_gz(path, merged)
    echo(f'{len(activities)} activities listed, {len(merged)} in the archive.')
    if start > DEFAULT_START:
        echo('Note: activities.csv.gz not updated for a partial range.')
        return activities
    try:
        write_gz(out / 'activities.csv.gz',
                 client.get(client.athlete_path('activities.csv'),
                            oldest=start, newest=_plus_one(end)))
    except ApiError as err:
        echo(f'Note: activities.csv.gz skipped ({err.status}).')
    return activities


def sync_per_activity(client, activities, directory, endpoint, *, label,
                      refresh_days=30, force=False, pause=0.15, params=None,
                      today=None, sleep=time.sleep, echo=_no_echo):
    """Fetch one file per activity; return ``(loaded, failed)``.

    Existing files are kept, except for activities of the last
    ``refresh_days`` days (notes are often edited afterwards) or with ``force``.
    """
    today = today or date.today()
    cutoff = (today - timedelta(days=refresh_days)).isoformat()
    todo = []
    for activity in activities:
        target = directory / f'{activity["id"]}.json.gz'
        recent = (activity.get('start_date_local') or '')[:10] >= cutoff
        if force or recent or not target.exists():
            todo.append(activity)
    echo(f'{len(todo)} {label} file(s) to fetch.')

    loaded = failed = 0
    for number, activity in enumerate(todo, 1):
        activity_id = activity['id']
        try:
            data = client.get_json(endpoint.format(id=activity_id), **(params or {}))
            write_json_gz(directory / f'{activity_id}.json.gz', data)
            loaded += 1
        except ApiError as err:
            failed += 1
            echo(f'  {activity_id}: {err.status}')
        if number % 100 == 0:
            echo(f'  {number}/{len(todo)}')
        sleep(pause)
    return loaded, failed


def archive_details(client, out, activities, **kwargs):
    loaded, failed = sync_per_activity(
        client, activities, out / 'activity-details', 'activity/{id}',
        label='detail', params={'intervals': 'true'}, **kwargs)
    return f'details: {loaded} fetched, {failed} failed', failed


def archive_messages(client, out, activities, **kwargs):
    loaded, failed = sync_per_activity(
        client, activities, out / 'activity-messages',
        'activity/{id}/messages', label='message', **kwargs)
    return f'messages: {loaded} fetched, {failed} failed', failed


def archive_events(client, out, start, end, echo=_no_echo):
    found = {}
    for first, last in date_chunks(start, end, EVENT_CHUNK_DAYS):
        data = client.get_json(client.athlete_path('events'),
                               oldest=first, newest=last)
        for event in data:
            if event.get('id') is not None:
                found[str(event['id'])] = event
    path = out / 'events.json.gz'
    events = merge_records(path, found.values(), start, end,
                           key=lambda e: str(e['id']), day=_start_day)
    events.sort(key=lambda e: (_start_day(e), str(e['id'])))
    write_json_gz(path, events)
    echo(f'{len(found)} events fetched, {len(events)} in the archive.')
    return f'{len(events)} events'


def archive_wellness(client, out, start, end, echo=_no_echo):
    records = {}
    for first, last in date_chunks(start, end, WELLNESS_CHUNK_DAYS):
        data = client.get_json(client.athlete_path('wellness'),
                               oldest=first, newest=last)
        for record in data:
            if record.get('id'):
                records[record['id']] = record
    path = out / 'wellness.json.gz'
    merged = merge_records(path, records.values(), start, end,
                           key=lambda r: r['id'], day=lambda r: r['id'])
    merged.sort(key=lambda r: r['id'])
    write_json_gz(path, merged)
    records = {r['id']: r for r in merged}

    csv_path = Path(out) / HRV_CSV_NAME
    # An earlier CSV may hold days that wellness.json.gz does not (yet): keep
    # every row outside the requested range.
    rows = {}
    if csv_path.is_file():
        with open(csv_path, newline='', encoding='utf-8') as fh:
            for row in list(csv.reader(fh))[1:]:
                if row and not start.isoformat() <= row[0] <= end.isoformat():
                    rows[row[0]] = row
    for day, record in records.items():
        values = (record.get('hrv'), record.get('hrvSDNN'), record.get('baevskySI'))
        if any(v is not None for v in values):
            rows[day] = [day] + ['' if v is None else v for v in values]
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with open(csv_path, 'w', newline='', encoding='utf-8') as fh:
        writer = csv.writer(fh)
        writer.writerow(['date', 'hrv_rmssd', 'hrv_sdnn', 'baevsky_si'])
        writer.writerows(rows[day] for day in sorted(rows))
    echo(f'{len(records)} wellness days in the archive, {len(rows)} days with HRV data in the CSV.')
    return f'{len(records)} wellness days'
