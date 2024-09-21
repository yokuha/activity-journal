# activity journal

This is a simple no-guarantee tool to create a journal of the notes of your own
intervals.icu activities.


# Installation

1. Download or clone this package from github.
2. Get your athlete ID and API key from the Developer settings at
   https://intervals.icu/settings and create/update
   `src/iicu_activity_journal/settings.py` with that info using the format from
   `settings-template.py`.
3. Run `pip install .` and you are set.

## Prerequisites

You'll obviously need access to an account at https://intervals.icu – preferably
your own or one of your client.

In addition, you need a current Python installation with common packages, see
`pyproject.toml` for details.


# Usage

Get your activities from i.icu and add them to your local database running
`iicu-activity-journal-update-data`.

Create a PDF file of the data using `iicu-activity-journal-create`; this script
creates a markdown file of the data. It can also pass this through `pandoc`,
using `LaTeX` to produce a PDF, which are thus necessary to obtain a PDF. The
markdown file is always generated.

Run these scripts with `-h` options to obtain some basic help and a list of
options.


# Further comments

If you have any ideas on how to improve `activity journal` please let me know
or, preferably, create a pull request for improvements.
