# activity journal

This is a simple no-guarantee tool to create a journal of the notes of your own
intervals.icu activities.


# Installation

1. Download or clone this package from github.
2. Get your athlete ID and API key from the Developer settings at
   https://intervals.icu/settings and either set the environment variables
   `INTERVALS_ICU_ATHLETE_ID` and `INTERVALS_ICU_API_KEY`, use a `.env` file,
   or add this entry to your encrypted `~/.authinfo.gpg` file:

   ```text
   machine intervals.icu login your-athlete-id password your-api-key
   ```

   Use an editor or password manager that decrypts and re-encrypts authinfo
   files without leaving a plaintext copy behind. Set `IICU_AUTHINFO_FILE` if
   your encrypted authinfo file is stored elsewhere.
3. Run `pip install .` and you are set.

## Prerequisites

You'll obviously need access to an account at https://intervals.icu – preferably
your own or one of your client.

In addition, you need a current Python installation with common packages, see
`pyproject.toml` for details, and, only if you use the authinfo file, GnuPG (`gpg`).


# Archive

`iicu-journal archive all` saves your intervals.icu data as reproducible,
gzip-compressed JSON files in the archive directory: `./archive` by default
(relative to the current directory), or whatever you give with `--archive-dir`
or the environment variable `IICU_ARCHIVE_DIR` (a full path is fine). Each run
adds one line to a logbook, by default `<archive dir>/logbook.md`; use
`--logbook` or `IICU_LOGBOOK` to write into another Markdown file, e.g. the
README of a private data repository. The command is read-only on the server
and incremental: existing per-activity files are kept, and files of the last 30
days are fetched again because notes are often edited afterwards.

It saves the athlete profile and sport settings, gear (including components),
activities with details and intervals, the notes/messages of every activity,
calendar events (notes, races, holidays, injuries, ...), and wellness data.
Single parts are available as `archive activities|messages|events|athlete|gear|wellness`.
FIT/GPX files and per-second streams are not included.

Credentials are looked up in the environment variables
`INTERVALS_ICU_ATHLETE_ID` and `INTERVALS_ICU_API_KEY`, then in a `.env` file
(`--env`, or `./.env`), then in the encrypted authinfo file described
above. Keep your archive directory outside this repository or in a private
repository; it contains personal data.


# Usage

1. Archive your data: `iicu-journal archive all` (see above).
2. Create the journal: `iicu-journal create`. It writes
   `journal-<athlete-id>.md` to `--output-dir` (default: current directory)
   and, via `pandoc` and LaTeX, a PDF of it (`--no-pandoc` for Markdown only).
   The LaTeX installation must include the `twemojis` package so Unicode emoji
   can be embedded as color vector artwork. All activities, calendar notes
   (notes, races, holidays, injuries, sickness) and the notes/messages of every
   activity are included; use `-c` to include commutes and `-b`/`-e` to limit
   the date range.
3. Optional: `iicu-journal duplicates` lists activities that start and end at
   about the same time, `iicu-journal create -i` lists restricted or incomplete
   activities (for example from Strava) that need to be fixed or imported at the
   source before they can appear in the journal.

Personal settings live in an optional TOML file (`--config`, `IICU_JOURNAL_CONFIG`
or `<archive dir>/journal.toml`):

```toml
author = "Your Name"        # shown in the document
show_email = false          # print your profile e-mail address in the journal
[name_aliases]              # display names of note authors
your-intervals-username = "JK"
```

Run any command with `-h` for all options.


# Further comments

If you have any ideas on how to improve `activity journal` please let me know
or, preferably, create a pull request for improvements.


## Requirements

Plotting L/R balance has further requirements, e.g., `matplotlib` and `scipy`.
However, as this functionality is now routinely available in intervals.icu I do
not want to impose these requirements on the general use of the activity
journal. If you want to use the `balance` command, install them with
`pip install "iicu_activity_journal[balance]"` and run
`iicu-journal balance -a <activity-id>`. For standard use, they are not needed.
