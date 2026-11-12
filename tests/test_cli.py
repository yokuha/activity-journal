from click.testing import CliRunner

from iicu_activity_journal import cli
from iicu_activity_journal.api import IntervalsClient
from iicu_activity_journal.store import read_json_gz
from tests.conftest import FakeSession


def test_archive_all_end_to_end(tmp_path, monkeypatch):
    routes = {
        '/profile': {'name': 'Test Athlete'},
        '/sport-settings': [],
        '/gear': [{'id': 'g1', 'name': 'Bike'}],
        '/activities.csv': [],
        '/activities': [{'id': 'i1', 'start_date_local': '2020-01-01T10:00:00'}],
        '/activity/i1': {'id': 'i1', 'name': 'Ride'},
        '/activity/i1/messages': [{'id': 1, 'content': 'IICU-TEST'}],
        '/events': [{'id': 5, 'category': 'NOTE', 'start_date_local': '2020-01-02T00:00:00'}],
        '/wellness': [{'id': '2020-01-01', 'hrv': 50}],
    }
    # Longest suffix first so '/activity/i1/messages' is not shadowed.
    routes = dict(sorted(routes.items(), key=lambda kv: -len(kv[0])))
    monkeypatch.setenv('INTERVALS_ICU_API_KEY', 'k')
    monkeypatch.setenv('INTERVALS_ICU_ATHLETE_ID', 'i7')
    monkeypatch.setattr(
        cli, 'IntervalsClient',
        lambda aid, key: IntervalsClient(aid, key, session=FakeSession(routes),
                                         sleep=lambda _s: None))

    result = CliRunner().invoke(cli.main, ['archive', 'all', '--archive-dir', str(tmp_path / 'arc'),
                                           '--start', '2020-01-01', '--end', '2020-01-31',
                                           '--pause', '0', '--refresh-days', '0'])
    assert result.exit_code == 0, result.output
    out = tmp_path / 'arc'
    assert read_json_gz(out / 'activity-messages' / 'i1.json.gz')[0]['content'] == 'IICU-TEST'
    assert read_json_gz(out / 'gear.json.gz')[0]['name'] == 'Bike'
    assert 'activities saved' in (tmp_path / 'arc' / 'logbook.md').read_text()


def test_missing_credentials_is_clean_error(tmp_path, monkeypatch):
    monkeypatch.delenv('INTERVALS_ICU_API_KEY', raising=False)
    monkeypatch.delenv('INTERVALS_ICU_ATHLETE_ID', raising=False)
    monkeypatch.setenv('IICU_AUTHINFO_FILE', str(tmp_path / 'none.gpg'))
    result = CliRunner().invoke(cli.main, ['archive', 'gear', '--archive-dir', str(tmp_path)])
    assert result.exit_code != 0 and 'No API key' in result.output
