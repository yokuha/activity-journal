from datetime import date, timedelta

from click.testing import CliRunner

from iicu_activity_journal import cli, render
from iicu_activity_journal.config import JournalConfig, load_config
from iicu_activity_journal.duplicates import find_duplicates
from iicu_activity_journal.entries import load_archive


def test_load_archive_merges_activities_events_and_messages(archive_dir):
    archive = load_archive(archive_dir)
    assert {e.id for e in archive.entries} == {'999', 'i10', 'i11', 'i12', 'i13', '77', '78'}
    assert 'WORKOUT' not in {e.category for e in archive.entries}
    ride = next(e for e in archive.entries if e.id == 'i10')
    assert [m.content for m in ride.messages] == ['IICU-FOOD\nWater: 1 l', 'photo']
    assert next(e for e in archive.entries if e.id == '999').incomplete
    assert archive.entries == sorted(archive.entries, key=lambda e: (e.start, e.id),
                                     reverse=True)


def test_load_archive_requires_activities(tmp_path):
    import pytest
    with pytest.raises(FileNotFoundError):
        load_archive(tmp_path)


def test_clean_note_removes_boilerplate_and_keeps_breaks():
    text = 'Hello\nworld\n-- myWindsock Report\nx\nEND --\npowered by icTrainer'
    assert render.clean_note(text) == 'Hello    \nworld'


def test_stats_line_ride_and_run(archive_dir):
    by_id = {e.id: e for e in load_archive(archive_dir).entries}
    assert render.stats_line(by_id['i10']) == (
        'RPE = 4, AP = 180 W, NP = 181 W, IF = 0.72 (FTP = 250), '
        'L/R = 49/51, calories = 900 kcal')
    assert render.stats_line(by_id['i12']) == (
        'RPE = —, IF = 0.60, calories = — kcal')
    assert render.stats_line(by_id['77']) is None


def test_journal_content(archive_dir, tmp_path):
    archive = load_archive(archive_dir)
    config = JournalConfig(name_aliases={'tester': 'T'}, show_email=False)
    mdf, incomplete = render.build_journal(archive, config, tmp_path / 'j.md')
    text = mdf.file_data_text
    assert [e.id for e in incomplete] == ['999']
    assert 'Morning ride' in text and 'To work' not in text      # commute hidden
    assert 'T: IICU-FOOD    \nWater: 1 l' in text                # alias + line break
    assert 'coach attached [photo](https://x/y.png)' in text
    assert 'gone' not in text and 'noise' not in text
    assert 'tester@example.org' not in text                      # email opt-in
    assert 'Mon 2026-04-20...Mon 2026-04-27' in text            # holiday range
    assert 'Waxed the chain' in text


def test_commute_and_date_range(archive_dir, tmp_path):
    archive = load_archive(archive_dir)
    mdf, _ = render.build_journal(archive, JournalConfig(), tmp_path / 'j.md',
                                  begin=date(2026, 5, 3), end=date(2026, 5, 3), commute=True)
    assert 'To work' in mdf.file_data_text and 'Morning ride' not in mdf.file_data_text


def test_config_file(tmp_path):
    path = tmp_path / 'journal.toml'
    path.write_text('author = "A"\nshow_email = true\n[name_aliases]\nx = "Y"\n')
    config = load_config(path)
    assert (config.author, config.show_email, config.display_name('x')) == ('A', True, 'Y')
    assert load_config(tmp_path / 'missing.toml') == JournalConfig()


def test_find_duplicates(archive_dir):
    entries = load_archive(archive_dir).entries
    pairs = find_duplicates(entries)
    assert [(a.id, b.id) for a, b in pairs] == [('i12', 'i13')]
    assert find_duplicates(entries, start_gap=timedelta(minutes=1)) == []


def test_create_command_writes_markdown(archive_dir, tmp_path):
    out = tmp_path / 'out'
    result = CliRunner().invoke(cli.main, [
        'create', '--archive-dir', str(archive_dir), '--output-dir', str(out),
        '--no-pandoc', '-i'])
    assert result.exit_code == 0, result.output
    assert 'Incomplete activity 999' in result.output
    assert (out / 'journal-i1.md').read_text().count('## ') >= 4


def test_duplicates_command(archive_dir):
    result = CliRunner().invoke(cli.main, ['duplicates', '--archive-dir', str(archive_dir)])
    assert result.exit_code == 0
    assert 'https://intervals.icu/activities/i12' in result.output
    assert 'Found 1 potential duplicate' in result.output
