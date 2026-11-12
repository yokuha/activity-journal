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


__all__ = ['FakeResponse', 'requests']
