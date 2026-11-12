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

"""Minimal read-only client for the intervals.icu API."""

import time

import requests

BASE_URL = 'https://intervals.icu/api/v1'
USER_AGENT = 'iicu-activity-journal (personal archive)'
RETRY_STATUS = {429, 500, 502, 503, 504}


class ApiError(RuntimeError):
    """An API request failed for good (after retries)."""

    def __init__(self, status, url, body=''):
        super().__init__(f'HTTP {status} for {url}: {body}'.rstrip(': '))
        self.status = status
        self.url = url


class IntervalsClient:
    """GET requests with basic auth, retries and rate-limit handling."""

    def __init__(self, athlete_id, api_key, *, session=None, base_url=BASE_URL,
                 retries=5, backoff=5.0, sleep=time.sleep):
        self.athlete_id = str(athlete_id)
        self._base_url = base_url.rstrip('/')
        self._retries = retries
        self._backoff = backoff
        self._sleep = sleep
        self._session = session or requests.Session()
        self._session.auth = ('API_KEY', api_key)
        self._session.headers['User-Agent'] = USER_AGENT

    def url(self, path):
        return f'{self._base_url}/{path.lstrip("/")}'

    def athlete_path(self, suffix=''):
        return f'athlete/{self.athlete_id}/{suffix}'.rstrip('/')

    @staticmethod
    def _retry_after(response, default):
        try:
            return float(response.headers.get('Retry-After'))
        except (TypeError, ValueError):
            return default

    def get(self, path, **params):
        """Return the response body (bytes) of a GET request."""
        url = self.url(path)
        params = {k: v for k, v in params.items() if v is not None}
        delay = self._backoff
        for attempt in range(self._retries + 1):
            last = attempt == self._retries
            try:
                response = self._session.get(url, params=params, timeout=120)
            except requests.RequestException as err:
                if last:
                    raise ApiError(0, url, str(err)) from None
                self._sleep(delay)
                delay *= 2
                continue
            if response.status_code == 200:
                return response.content
            if response.status_code in RETRY_STATUS and not last:
                self._sleep(self._retry_after(response, delay))
                delay *= 2
                continue
            raise ApiError(response.status_code, url, response.text[:300])
        raise ApiError(0, url, 'unreachable')  # pragma: no cover

    def get_json(self, path, **params):
        import json
        return json.loads(self.get(path, **params))
