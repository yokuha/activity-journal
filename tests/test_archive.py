import csv
from datetime import date

from iicu_activity_journal import archive as ar
from iicu_activity_journal.store import read_json_gz


def test_date_chunks_cover_range_without_overlap():
    chunks = list(ar.date_chunks(date(2020, 1, 1), date(2020, 1, 10), 4))
    assert chunks == [(date(2020, 1, 1), date(2020, 1, 4)),
                      (date(2020, 1, 5), date(2020, 1, 8)),
                      (date(2020, 1, 9), date(2020, 1, 10))]


def test_activities_sorted_and_deduplicated(make_client, tmp_path):
    rows = [{'id': 'i2', 'start_date_local': '2020-02-01T00:00:00'},
            {'id': 'i1', 'start_date_local': '2020-01-01T00:00:00'},
            {'id': 'i2', 'start_date_local': '2020-02-01T00:00:00'}]
    client, _ = make_client({'/activities': rows, '/activities.csv': []})
    result = ar.archive_activities(client, tmp_path, date(2020, 1, 1), date(2020, 3, 1))
    assert [a['id'] for a in result] == ['i1', 'i2']
    assert [a['id'] for a in read_json_gz(tmp_path / 'activities.json.gz')] == ['i1', 'i2']


def test_per_activity_refresh_rules(make_client, tmp_path, activities):
    directory = tmp_path / 'activity-messages'
    client, session = make_client({'/messages': [{'id': 1, 'content': 'hello'}]})
    today = date(2026, 11, 12)
    kwargs = dict(label='message', pause=0, today=today, sleep=lambda _s: None)
    endpoint = 'activity/{id}/messages'

    loaded, failed = ar.sync_per_activity(client, activities, directory, endpoint, **kwargs)
    assert (loaded, failed) == (2, 0)
    assert read_json_gz(directory / 'i1.json.gz')[0]['content'] == 'hello'

    # Second run: only the recent activity is fetched again.
    session.calls.clear()
    loaded, _ = ar.sync_per_activity(client, activities, directory, endpoint, **kwargs)
    assert loaded == 1 and 'i2' in session.calls[0][0]

    # --force fetches everything.
    loaded, _ = ar.sync_per_activity(client, activities, directory, endpoint,
                                     force=True, **kwargs)
    assert loaded == 2


def test_failed_fetch_is_counted_not_fatal(make_client, tmp_path, activities):
    client, _ = make_client({})  # everything 404
    loaded, failed = ar.sync_per_activity(
        client, activities, tmp_path / 'd', 'activity/{id}', label='detail',
        pause=0, sleep=lambda _s: None)
    assert (loaded, failed) == (0, 2)


def test_events_and_gear_saved_sorted(make_client, tmp_path):
    client, _ = make_client({
        '/events': [{'id': 2, 'category': 'NOTE', 'start_date_local': '2021-01-01T00:00:00'},
                    {'id': 1, 'category': 'HOLIDAY', 'start_date_local': '2020-01-01T00:00:00'}],
        '/gear': [{'id': 'g2', 'name': 'Z'}, {'id': 'g1', 'name': 'A', 'distance': 1234}],
    })
    ar.archive_events(client, tmp_path, date(2020, 1, 1), date(2021, 1, 1))
    assert [e['id'] for e in read_json_gz(tmp_path / 'events.json.gz')] == [1, 2]
    ar.archive_gear(client, tmp_path)
    assert [g['id'] for g in read_json_gz(tmp_path / 'gear.json.gz')] == ['g1', 'g2']


def test_wellness_csv_only_rows_with_hrv(make_client, tmp_path):
    client, _ = make_client({'/wellness': [
        {'id': '2024-01-02', 'hrv': 55.5, 'baevskySI': 80},
        {'id': '2024-01-01', 'weight': 70},
    ]})
    ar.archive_wellness(client, tmp_path, date(2024, 1, 1), date(2024, 1, 2))
    assert len(read_json_gz(tmp_path / 'wellness.json.gz')) == 2
    with open(tmp_path / ar.HRV_CSV_NAME, newline='', encoding='utf-8') as fh:
        rows = list(csv.reader(fh))
    assert rows == [['date', 'hrv_rmssd', 'hrv_sdnn', 'baevsky_si'],
                    ['2024-01-02', '55.5', '', '80']]
