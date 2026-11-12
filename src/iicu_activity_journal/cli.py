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

"""Command line interface: ``iicu-journal``."""

import functools
import sys
from datetime import date, timedelta
from pathlib import Path

import click

from iicu_activity_journal import archive as ar
from iicu_activity_journal import render
from iicu_activity_journal.api import ApiError, IntervalsClient
from iicu_activity_journal.config import load_config
from iicu_activity_journal.credentials import CredentialsError, load_credentials
from iicu_activity_journal.duplicates import find_duplicates
from iicu_activity_journal.entries import load_archive
from iicu_activity_journal.store import append_logbook


def _iso_date(_ctx, _param, value):
    if value is None or isinstance(value, date):
        return value
    try:
        return date.fromisoformat(value)
    except ValueError:
        raise click.BadParameter('use the format YYYY-MM-DD') from None


def _archive_dir_option(func):
    return click.option(
        '--archive-dir', envvar='IICU_ARCHIVE_DIR', default='archive',
        show_default=True, type=click.Path(file_okay=False),
        help='Directory of the archived data; relative paths are relative to '
             'the current directory.')(func)


def _common_options(func):
    func = _archive_dir_option(func)

    options = [
        click.option('--env', 'env_file', type=click.Path(dir_okay=False),
                     help='.env file with INTERVALS_ICU_API_KEY and '
                          'INTERVALS_ICU_ATHLETE_ID (default: ./.env, then '
                          'authinfo).'),
        click.option('--logbook', envvar='IICU_LOGBOOK', type=click.Path(dir_okay=False),
                     help='Markdown file whose "# logbook" section receives one '
                          'line per run (default: <archive dir>/logbook.md).'),
        click.option('--no-log', is_flag=True,
                     help='Do not append an entry to the logbook.'),
    ]
    for option in reversed(options):
        func = option(func)
    return func


def _range_options(func):
    options = [
        click.option('-b', '--start', default=str(ar.DEFAULT_START),
                     show_default=True, callback=_iso_date,
                     help='First date, YYYY-MM-DD.'),
        click.option('-e', '--end', default=lambda: str(date.today()),
                     show_default='today', callback=_iso_date,
                     help='Last date, YYYY-MM-DD.'),
    ]
    for option in reversed(options):
        func = option(func)
    return func


def _fetch_options(func):
    options = [
        click.option('--refresh-days', default=30, show_default=True,
                     help='Fetch files of the last N days again.'),
        click.option('--force', is_flag=True, help='Fetch all files again.'),
        click.option('--pause', default=0.15, show_default=True,
                     help='Seconds between requests.'),
    ]
    for option in reversed(options):
        func = option(func)
    return func


class Session:
    """What the archive commands share: client, output dir, logging."""

    def __init__(self, archive_dir, env_file, logbook, no_log):
        self.out = Path(archive_dir).expanduser()
        self.logbook = (Path(logbook).expanduser() if logbook
                        else self.out / 'logbook.md')
        self.no_log = no_log
        try:
            credentials = load_credentials(env_file, Path.cwd())
        except CredentialsError as err:
            raise click.ClickException(str(err)) from err
        self.client = IntervalsClient(credentials.athlete_id, credentials.api_key)
        self.summary = []
        self.failed = 0

    def echo(self, message):
        click.echo(message)

    def finish(self):
        if self.summary and not self.no_log:
            line = f'{date.today()} ' + '; '.join(self.summary)
            append_logbook(self.logbook, line)
            click.echo(f'Logbook entry appended to {self.logbook}.')
        if self.failed:
            raise click.ClickException(f'{self.failed} request(s) failed.')


def _guard(func):
    """Turn API errors into clean CLI errors."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ApiError as err:
            raise click.ClickException(str(err)) from err
        except FileNotFoundError as err:
            raise click.ClickException(str(err)) from err
    return wrapper


def _run_activities(session, start, end, no_details, fetch_kwargs):
    activities = ar.archive_activities(session.client, session.out, start, end,
                                      session.echo)
    span = ''
    if activities:
        days = [a['start_date_local'][:10] for a in activities
                if a.get('start_date_local')]
        if days:
            span = f' ({min(days)} to {max(days)})'
    session.summary.append(f'{len(activities)} activities saved{span}')
    if not no_details:
        text, failed = ar.archive_details(session.client, session.out, activities,
                                         echo=session.echo, **fetch_kwargs)
        session.summary.append(text)
        session.failed += failed
    return activities


@click.group()
@click.help_option('--help', '-h')
def main():
    """Create a journal from your intervals.icu data."""


@main.group()
@click.help_option('--help', '-h')
def archive():
    """Archive intervals.icu data to local files (read-only on the server)."""


@archive.command('all')
@_common_options
@_range_options
@_fetch_options
@click.option('--no-details', is_flag=True,
              help='Do not fetch per-activity detail files.')
@_guard
def archive_all(archive_dir, env_file, logbook, no_log, start, end, refresh_days, force,
               pause, no_details):
    """Archive everything: athlete, gear, activities, notes, events, wellness."""
    session = Session(archive_dir, env_file, logbook, no_log)
    fetch_kwargs = dict(refresh_days=refresh_days, force=force, pause=pause)
    session.summary.append(ar.archive_athlete(session.client, session.out, session.echo))
    session.summary.append(ar.archive_gear(session.client, session.out, session.echo))
    activities = _run_activities(session, start, end, no_details, fetch_kwargs)
    text, failed = ar.archive_messages(session.client, session.out, activities,
                                      echo=session.echo, **fetch_kwargs)
    session.summary.append(text)
    session.failed += failed
    for func in (ar.archive_events, ar.archive_wellness):
        session.summary.append(func(session.client, session.out, start, end, session.echo))
    session.finish()


@archive.command('activities')
@_common_options
@_range_options
@_fetch_options
@click.option('--no-details', is_flag=True,
              help='Do not fetch per-activity detail files.')
@_guard
def archive_activities_cmd(archive_dir, env_file, logbook, no_log, start, end,
                          refresh_days, force, pause, no_details):
    """Archive the activity list and the per-activity details."""
    session = Session(archive_dir, env_file, logbook, no_log)
    _run_activities(session, start, end, no_details,
                    dict(refresh_days=refresh_days, force=force, pause=pause))
    session.finish()


@archive.command('messages')
@_common_options
@_fetch_options
@_guard
def archive_messages_cmd(archive_dir, env_file, logbook, no_log, refresh_days, force, pause):
    """Archive the notes/messages of every activity in the saved list."""
    session = Session(archive_dir, env_file, logbook, no_log)
    activities = ar.load_activities(session.out)
    text, failed = ar.archive_messages(session.client, session.out, activities,
                                      echo=session.echo, refresh_days=refresh_days,
                                      force=force, pause=pause)
    session.summary.append(text)
    session.failed += failed
    session.finish()


@archive.command('events')
@_common_options
@_range_options
@_guard
def archive_events_cmd(archive_dir, env_file, logbook, no_log, start, end):
    """Archive calendar events (notes, races, holidays, injuries, ...)."""
    session = Session(archive_dir, env_file, logbook, no_log)
    session.summary.append(ar.archive_events(session.client, session.out, start, end, session.echo))
    session.finish()


@archive.command('athlete')
@_common_options
@_guard
def archive_athlete_cmd(archive_dir, env_file, logbook, no_log):
    """Archive the athlete profile and sport settings."""
    session = Session(archive_dir, env_file, logbook, no_log)
    session.summary.append(ar.archive_athlete(session.client, session.out, session.echo))
    session.finish()


@archive.command('gear')
@_common_options
@_guard
def archive_gear_cmd(archive_dir, env_file, logbook, no_log):
    """Archive the gear list."""
    session = Session(archive_dir, env_file, logbook, no_log)
    session.summary.append(ar.archive_gear(session.client, session.out, session.echo))
    session.finish()


@archive.command('wellness')
@_common_options
@_range_options
@_guard
def archive_wellness_cmd(archive_dir, env_file, logbook, no_log, start, end):
    """Archive wellness data (plus an HRV/Baevsky CSV)."""
    session = Session(archive_dir, env_file, logbook, no_log)
    session.summary.append(
        ar.archive_wellness(session.client, session.out, start, end, session.echo))
    session.finish()


def _optional_date(ctx, param, value):
    return _iso_date(ctx, param, value) if value else None


@main.command('create')
@_archive_dir_option
@click.option('--config', 'config_file', envvar='IICU_JOURNAL_CONFIG',
              type=click.Path(dir_okay=False),
              help='TOML file with personal settings (default: '
                   '<archive dir>/journal.toml if it exists).')
@click.option('--output-dir', default='.', show_default=True,
              type=click.Path(file_okay=False), help='Where to write the journal.')
@click.option('-b', '--begin', callback=_optional_date, help='First date, YYYY-MM-DD.')
@click.option('-e', '--end', callback=_optional_date, help='Last date, YYYY-MM-DD.')
@click.option('-c', '--commute', is_flag=True, help='Include commutes.')
@click.option('--pandoc/--no-pandoc', 'use_pandoc', default=True, show_default=True,
              help='Create a PDF with pandoc/LaTeX; otherwise only Markdown.')
@click.option('-v', '--verbose', is_flag=True, help='Include the athlete bio.')
@click.option('-i', '--report-incomplete', is_flag=True,
              help='List activities whose details are unavailable.')
@_guard
def create_cmd(archive_dir, config_file, output_dir, begin, end, commute,
               use_pandoc, verbose, report_incomplete):
    """Create the journal (Markdown and PDF) from the archive."""
    archive_path = Path(archive_dir).expanduser()
    archive = load_archive(archive_path)
    config = load_config(config_file or archive_path / 'journal.toml')
    athlete_id = archive.athlete.get('id', 'unknown')
    out = Path(output_dir).expanduser()
    out.mkdir(parents=True, exist_ok=True)
    md_path = out / f'journal-{athlete_id}.md'

    mdf, incomplete = render.build_journal(
        archive, config, md_path, begin=begin, end=end, commute=commute,
        verbose=verbose)
    mdf.create_md_file()
    click.echo(f'Markdown written to {md_path}.')
    if report_incomplete:
        for entry in incomplete:
            click.echo(
                f'Incomplete activity {entry.id} on {entry.start:%Y-%m-%d %H:%M}: '
                'Intervals.icu supplied no name or activity details. Import/fix '
                'the source data if it should appear in the journal: '
                f'https://intervals.icu/activities/{entry.id}')
        click.echo(f'Found {len(incomplete)} incomplete activity record(s).')
    if archive.skipped:
        click.echo(f'Skipped {archive.skipped} record(s) without a start date.')
    if use_pandoc:
        try:
            render.run_pandoc(md_path, md_path.with_suffix('.pdf'))
        except RuntimeError as err:
            raise click.ClickException(str(err)) from err
        click.echo(f'PDF written to {md_path.with_suffix(".pdf")}.')


@main.command('duplicates')
@_archive_dir_option
@click.option('-b', '--begin', callback=_optional_date, help='First date, YYYY-MM-DD.')
@click.option('-e', '--end', callback=_optional_date, help='Last date, YYYY-MM-DD.')
@click.option('-c', '--commute', is_flag=True, help='Include commutes.')
@click.option('--start-gap', default=15, show_default=True,
              help='Maximum difference of start times in minutes.')
@click.option('--duration-gap', default=15, show_default=True,
              help='Maximum difference of durations in minutes.')
@_guard
def duplicates_cmd(archive_dir, begin, end, commute, start_gap, duration_gap):
    """Search the archive for potential duplicate activities."""
    archive = load_archive(Path(archive_dir).expanduser())
    entries = [e for e in archive.entries
               if render.in_range(e, begin, end) and (commute or not e.commute)]
    pairs = find_duplicates(entries, start_gap=timedelta(minutes=start_gap),
                            duration_gap=timedelta(minutes=duration_gap))
    for first, second in pairs:
        click.echo('\nPotential duplicates:')
        for entry in (first, second):
            click.echo(entry.link or f'No i.icu link available for {entry.id}')
    click.echo(f'\nFound {len(pairs)} potential duplicate(s).')


@main.command('balance')
@click.option('-a', '--activity', 'activity_id', required=True, help='Activity ID.')
@click.option('-o', '--output', type=click.Path(dir_okay=False),
              help='PNG file (default: ./balance-<activity>.png).')
@click.option('--show', is_flag=True, help='Also open an interactive plot window.')
@click.option('--env', 'env_file', type=click.Path(dir_okay=False),
              help='.env file with the credentials (default: ./.env, then authinfo).')
@_guard
def balance_cmd(activity_id, output, show, env_file):
    """Plot the left/right power balance of an activity (needs the `balance` extra)."""
    try:
        from iicu_activity_journal.balance import plot_balance
    except ImportError as err:
        raise click.ClickException(
            'Install the extra requirements: pip install "iicu_activity_journal[balance]"'
        ) from err
    session = Session('.', env_file, None, True)
    target = Path(output) if output else Path(f'balance-{activity_id}.png')
    try:
        plot_balance(session.client, activity_id, target, show)
    except RuntimeError as err:
        raise click.ClickException(str(err)) from err
    click.echo(f'Plot written to {target}.')


if __name__ == '__main__':
    sys.exit(main())
