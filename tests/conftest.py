"""Shared test helpers: a fake HTTP session with synthetic intervals.icu data."""

import json

import pytest
import requests


class FakeResponse:
    def __init__(self, status=200, payload=None, headers=None):
        self.status_code = status
        self.headers = headers or {}
        self.content = json.dumps(payload).encode() if payload is not None else b''
        self.text = self.content.decode()


class Seq(list):
    """Successive responses for one route (the last one repeats)."""


class FakeSession:
    """Maps URL suffixes to responses (or lists of responses, used in order)."""

    def __init__(self, routes):
        self.routes = routes
        self.calls = []
        self.auth = None
        self.headers = {}

    def get(self, url, params=None, timeout=None):
        self.calls.append((url, params))
        for suffix, response in self.routes.items():
            if url.endswith(suffix):
                if isinstance(response, Seq):
                    item = response.pop(0) if len(response) > 1 else response[0]
                else:
                    item = response
                if isinstance(item, Exception):
                    raise item
                return item if isinstance(item, FakeResponse) else FakeResponse(payload=item)
        return FakeResponse(404, {'error': 'not found'})


@pytest.fixture
def activities():
    return [
        {'id': 'i1', 'start_date_local': '2020-01-05T10:00:00', 'name': 'Old ride'},
        {'id': 'i2', 'start_date_local': '2026-11-01T08:00:00', 'name': 'Recent ride'},
    ]


@pytest.fixture
def make_client():
    from iicu_activity_journal.api import IntervalsClient

    def make(routes):
        session = FakeSession(routes)
        client = IntervalsClient('i123', 'secret', session=session,
                                 sleep=lambda _s: None)
        return client, session

    return make


@pytest.fixture
def archive_dir(tmp_path):
    """A small synthetic archive (no real data)."""
    from iicu_activity_journal.store import write_json_gz

    root = tmp_path / 'archive'
    write_json_gz(root / 'athlete.json.gz', {'athlete': {
        'id': 'i1', 'name': 'tester', 'email': 'tester@example.org', 'bio': 'Line one\nLine two'}})
    write_json_gz(root / 'activities.json.gz', [
        {'id': 'i10', 'type': 'Ride', 'name': 'Morning ride', 'commute': False,
         'start_date_local': '2026-05-02T08:00:00', 'elapsed_time': 5400,
         'description': 'Nice day\nsecond line\n-- myWindsock Report\nnoise\nEND --',
         'icu_average_watts': 180, 'icu_ftp': 250, 'icu_intensity': 72.4,
         'avg_lr_balance': 51.2, 'icu_rpe': 4, 'calories': 900, 'tags': ['Outdoor']},
        {'id': 'i11', 'type': 'Ride', 'name': 'To work', 'commute': True,
         'start_date_local': '2026-05-03T07:00:00', 'elapsed_time': 1200},
        {'id': 'i12', 'type': 'Run', 'name': 'Easy run', 'commute': False,
         'start_date_local': '2026-05-04T18:00:00', 'elapsed_time': 3000,
         'icu_intensity': 60.0},
        {'id': 'i14', 'type': 'WeightTraining', 'name': 'Strength', 'commute': False,
         'start_date_local': '2026-05-06T07:00:00', 'elapsed_time': 2400,
         'tags': ['Kraft', 'Reha']},
        {'id': 'i15', 'type': 'Workout', 'name': 'Core', 'commute': False,
         'start_date_local': '2026-05-07T07:00:00', 'elapsed_time': 900, 'tags': ['kraft']},
        {'id': '999', 'start_date_local': '2026-05-05T09:00:00',
         '_note': 'STRAVA activities are not available via the API'},
        {'id': 'i13', 'type': 'Run', 'name': 'Same run again', 'commute': False,
         'start_date_local': '2026-05-04T18:05:00', 'elapsed_time': 3010},
    ])
    write_json_gz(root / 'activity-messages' / 'i10.json.gz', [
        {'id': 1, 'name': 'tester', 'content': 'IICU-FOOD\nWater: 1 l', 'deleted': False},
        {'id': 2, 'name': 'coach', 'content': 'photo', 'attachment_url': 'https://x/y.png'},
        {'id': 3, 'name': 'coach', 'content': 'gone', 'deleted': True},
    ])
    write_json_gz(root / 'events.json.gz', [
        {'id': 77, 'category': 'NOTE', 'name': 'Chain waxed',
         'start_date_local': '2026-05-01T00:00:00', 'end_date_local': '2026-05-01T00:00:00',
         'description': 'Waxed the chain'},
        {'id': 78, 'category': 'HOLIDAY', 'name': 'Trip',
         'start_date_local': '2026-04-20T00:00:00', 'end_date_local': '2026-04-27T00:00:00'},
        {'id': 79, 'category': 'WORKOUT', 'name': 'Planned',
         'start_date_local': '2026-05-09T00:00:00'},
    ])
    return root


__all__ = ['FakeResponse', 'requests']
