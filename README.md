# activity journal

This is a simple no-guarantee tool to create a journal of the notes of your own
intervals.icu activities.


# Installation

None (yet). For now, clone the git repository and run the scripts.

## Prerequisites

You'll obviously need access to an account at https://intervals.icu – preferably
your own or one of your client.

In addition, you need a current Python installation with common packages, most
noteworthy are probably

* json
* matplotlib
* mdUtils
* requests
* scipy


# Usage

1. Get your athlete ID and API key from the Developer settings at
   https://intervals.icu/settings and create/update `settings.py` with that
   info using the format from `settings-template.py`.
2. Get your activities from i.icu and add them to your local database running
   `update-data.py`.
3. Create a PDF file of the data using `activity-journal.py`; this script
   creates a markdown file of the data and passes this through `pandoc`, which
   is thus necessary.


# Further comments

If you have any ideas on how to improve `activity journal` please let me know
or, preferably, create a pull request for improvements.
