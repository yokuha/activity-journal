# activity journal

This is a simple no-guarantee tool to create a journal of the notes of your own
intervals.icu activities.


# Installation

1. Download or clone this package from github.
2. Get your athlete ID and API key from the Developer settings at
   https://intervals.icu/settings and add this entry to your encrypted
   `~/.authinfo.gpg` file:

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
`pyproject.toml` for details, and GnuPG (`gpg`) to decrypt the authinfo file.


# Usage

Get your activities from i.icu and add them to your local database running
`iicu-activity-journal-update-data`. By default, the updater removes local
records inside the requested date range when Intervals.icu no longer returns
them. Complete records are merged by ID into
`logbook-<athlete-id>-historic-activity-data.json`; incomplete records without
a name are deleted. Pass `--keep-missing` to retain both kinds of missing
records in the active activity-data file instead.

Create a PDF file of the data using `iicu-activity-journal-create`; this script
creates a markdown file of the data. It can also pass this through `pandoc`,
using `LaTeX` to produce a PDF, which are thus necessary to obtain a PDF. The
markdown file is always generated. The LaTeX installation must include the
`twemojis` package so Unicode emoji can be embedded as color vector artwork.

Run these scripts with `-h` options to obtain some basic help and a list of
options. Pass `-i`/`--report-incomplete` to `iicu-activity-journal-create` to list
restricted or incomplete activities that need to be fixed or imported at the
source before they can appear in the journal.


# Further comments

If you have any ideas on how to improve `activity journal` please let me know
or, preferably, create a pull request for improvements.


## Requirements

Plotting L/R balance has further requirements, e.g., `matplotlib` and `scipy`.
However, as this functionality is now routinely available in intervals.icu I do
not want to impose these requirements on the general use of the activity
journal. If you want to use the `...-balance` script, make sure to install these
requirements manually. For standard use, they are not needed.
