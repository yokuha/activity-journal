import pytest
import requests

from iicu_activity_journal.api import ApiError
from tests.conftest import FakeResponse, Seq


def test_get_json_and_params_without_none(make_client):
    client, session = make_client({'/ping': {'ok': True}})
    assert client.get_json('ping', a=1, b=None) == {'ok': True}
    assert session.calls[0][1] == {'a': 1}
    assert session.auth == ('API_KEY', 'secret')


def test_retries_on_rate_limit(make_client):
    client, session = make_client({'/x': Seq([FakeResponse(429, headers={'Retry-After': '1'}),
                                              FakeResponse(payload=[1])])})
    assert client.get_json('x') == [1]
    assert len(session.calls) == 2


def test_gives_up_after_retries(make_client):
    client, session = make_client({'/x': FakeResponse(503, {'e': 1})})
    with pytest.raises(ApiError) as err:
        client.get('x')
    assert err.value.status == 503
    assert len(session.calls) == 6


def test_client_error_is_not_retried(make_client):
    client, session = make_client({})
    with pytest.raises(ApiError) as err:
        client.get('missing')
    assert err.value.status == 404
    assert len(session.calls) == 1


def test_network_error_becomes_api_error(make_client):
    client, _ = make_client({'/x': requests.ConnectionError('down')})
    with pytest.raises(ApiError) as err:
        client.get('x')
    assert err.value.status == 0
