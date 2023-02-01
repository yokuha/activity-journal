# activity journal

This is a simple no-guarantee tool to create a journal of the notes of your own
Strava activities.

# Installation

None. For now, clone the git repository and run the scripts.

# Usage

1. Make sure you have a local copy of your access token. Can get one using
`get-token.py`.

2. Get your latest activities from Strava and add them to your local database
running `update-data.py`.

3. Create a markdown file of the data using `activity-journal.py`.

4. Convert the markdown to, e.g., PDF using `pandoc ...`


# Further comments

Lot's to do, ... as my time allows;-)
- get all (updated) activities from a specified date on
- nicer output

If you have any ideas on how to improve `activity journal` please let me know
or, preferably, create a pull request for improvements.
