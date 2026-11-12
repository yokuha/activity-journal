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

"""Markdown rendering of the journal."""

import re
import shutil
import subprocess
from datetime import timedelta
from pathlib import Path

from mdutils.mdutils import MdUtils

from iicu_activity_journal import pandoc_config_file, pandoc_emoji_filter_file

# Boilerplate appended by third-party services; removed from descriptions.
# The patterns match across lines.
NOISE_PATTERNS = [
    r'-- myWindsock\.com Report.*END --',
    r'-- myWindsock Report.*END --',
    r'[\U0001F44F\U0001F44D].*-- From Wandrer\.earth',
    r'[\U0001F44F\U0001F44D].*-- From Wandrer',
    r'powered by icTrainer',
    r'-- Intervals icu.*[0-9]%',
]
DASH = '—'
HARD_BREAK = '    \n'


def clean_note(text):
    """Strip service boilerplate and keep line breaks in Markdown."""
    for pattern in NOISE_PATTERNS:
        text = re.sub(pattern, '', text, flags=re.DOTALL)
    return text.strip().replace('\r', '').replace('\n', HARD_BREAK)


def _number(value, fmt='{:.0f}'):
    return fmt.format(value) if value is not None else DASH


def _lr(entry):
    if entry.lr_balance is None:
        return DASH
    right = entry.lr_balance
    return f'{round(100 - right)}/{round(right)}'


def _normalized_power(entry):
    if entry.ftp is None or entry.intensity is None:
        return DASH
    return f'{entry.ftp * entry.intensity / 100:.0f}'


def _intensity(entry):
    return _number(entry.intensity and entry.intensity / 100, '{:.2f}')


def stats_line(entry):
    """Basic numbers of an activity; ``None`` if it has no type."""
    if not entry.type:
        return None
    rpe = _number(entry.rpe)
    calories = _number(entry.calories)
    if 'Ride' in entry.type:
        return (f'RPE = {rpe}, AP = {_number(entry.avg_power)} W, '
                f'NP = {_normalized_power(entry)} W, '
                f'IF = {_intensity(entry)} (FTP = {_number(entry.ftp)}), '
                f'L/R = {_lr(entry)}, calories = {calories} kcal')
    return f'RPE = {rpe}, IF = {_intensity(entry)}, calories = {calories} kcal'


def _duration(entry):
    if not entry.duration:
        return ''
    hours_minutes = str(timedelta(seconds=int(entry.duration))).rsplit(':', 1)[0]
    return f' ({hours_minutes} h)'


def when(entry):
    """Date/time line below the title."""
    start, end = entry.start, entry.end
    if entry.kind == 'event':
        if end and end.date() > start.date():
            return f'{start:%a %Y-%m-%d}...{end:%a %Y-%m-%d}'
        return f'{start:%a %Y-%m-%d}'
    if end and end.date() != start.date():
        return f'{start:%a %Y-%m-%d}...{end:%a %Y-%m-%d}{_duration(entry)}'
    return f'{start:%a %Y-%m-%d %H:%M} h{_duration(entry)}'


def in_range(entry, begin, end):
    day = entry.start.date()
    return (begin is None or day >= begin) and (end is None or day <= end)


def selected(entry, types=(), tags=(), with_events=False):
    """Apply the type/tag selection.

    Within ``types`` and within ``tags`` any match is enough, an entry has to
    satisfy both lists if both are given (case-insensitive). With a selection,
    calendar events are only kept if ``with_events`` is set.
    """
    if not types and not tags:
        return True
    if entry.kind == 'event':
        return with_events
    if types and entry.type.lower() not in {t.lower() for t in types}:
        return False
    return not tags or bool({t.lower() for t in tags} & {t.lower() for t in entry.tags})


def _slug(text):
    return re.sub(r'[^a-z0-9]+', '', text.lower())


def selection_suffix(types=(), tags=()):
    """File name suffix for a selection, e.g. ``-weighttraining-tag-kraft``."""
    parts = [_slug(t) for t in types] + [f'tag-{_slug(t)}' for t in tags]
    return ''.join(f'-{part}' for part in parts)


def build_journal(archive, config, md_path, *, begin=None, end=None,
                  commute=False, verbose=False, types=(), tags=(),
                  with_events=False):
    """Create the Markdown document; return ``(MdUtils, incomplete entries)``."""
    athlete = archive.athlete
    name = athlete.get('name', 'unknown')
    athlete_id = athlete.get('id', '')
    mdf = MdUtils(file_name=str(Path(md_path).with_suffix('')),
                  title=f'Activity journal of athlete {name} (id: {athlete_id})',
                  author=config.author)
    if athlete_id:
        mdf.new_paragraph(f'https://intervals.icu/athlete/{athlete_id}/fitness\n')
    if not commute:
        mdf.new_paragraph('(Without commutes; specify `-c` if you want commutes '
                          'to be included.)')
    if types or tags:
        chosen = [f'type {", ".join(types)}'] if types else []
        chosen += [f'tag {", ".join(tags)}'] if tags else []
        mdf.new_paragraph(f'(Selection: {"; ".join(chosen)}.)')
    if config.show_email and athlete.get('email'):
        mdf.new_paragraph(athlete['email'])
    if verbose and athlete.get('bio'):
        mdf.new_header(level=1, title='Story')
        mdf.new_paragraph(athlete['bio'].replace('\n', HARD_BREAK))
    mdf.new_paragraph('---')

    mdf.new_header(level=1, title='Activities')
    incomplete = []
    for entry in archive.entries:
        if not in_range(entry, begin, end):
            continue
        if not selected(entry, types, tags, with_events):
            continue
        if entry.kind == 'activity' and entry.incomplete:
            incomplete.append(entry)
            continue
        if entry.kind == 'activity' and entry.commute and not commute:
            continue
        _render_entry(mdf, entry, config)
    return mdf, incomplete


def _render_entry(mdf, entry, config):
    mdf.new_header(level=2, title=entry.name or entry.category)
    mdf.new_header(level=3, title=when(entry))
    if entry.link:
        mdf.new_paragraph(f'{entry.link}\n')
    elif entry.kind == 'activity':
        mdf.new_paragraph(f'No i.icu link available for {entry.id}; '
                          'feature is requested upstream.\n')
    if entry.kind == 'activity':
        stats = stats_line(entry)
        if stats:
            mdf.new_paragraph(stats + '\n')
    note = clean_note(entry.note)
    if note:
        mdf.new_header(level=3, title='Description')
        mdf.new_paragraph(note + '\n')
    if entry.messages:
        mdf.new_header(level=3, title='Notes/messages and links to files')
        for message in entry.messages:
            who = config.display_name(message.name)
            if message.attachment_url:
                mdf.new_paragraph(
                    f'{who} attached [{message.content}]({message.attachment_url})')
            else:
                mdf.new_paragraph(f'{who}: {message.content.strip().replace(chr(10), HARD_BREAK)}')
    mdf.new_paragraph('---')


def run_pandoc(md_path, pdf_path):
    """Create the PDF with pandoc/XeLaTeX; raise ``RuntimeError`` on failure."""
    if shutil.which('pandoc') is None:
        raise RuntimeError('pandoc is required to create the PDF '
                           '(or use --no-pandoc).')
    result = subprocess.run(
        ['pandoc', '-d', str(pandoc_config_file),
         '--lua-filter', str(pandoc_emoji_filter_file),
         '-o', str(pdf_path), str(md_path)],
        check=False)
    if result.returncode != 0:
        raise RuntimeError(f'pandoc failed with exit code {result.returncode}.')
