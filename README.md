# activity journal

This is a simple no-guarantee tool to create a journal of the notes of your own
Strava activities.

# Installation

None. For now, clone the git repository and run the scripts.

# Usage

2. Get your latest activities from Strava and add them to your local database
running `update-data.py`. If necessary, i.e., the first time, this will g
through a somewhat cumbersome process of getting you a Strava access token,
which you have to manually copy from the redirect URL after authorization to the
command line...

3. Create a markdown file of the data using `activity-journal.py`.

4. Convert the markdown to, e.g., PDF using `pandoc ...`


# Further comments

Lot's to do, ... as my time allows;-)
- get all (updated) activities from a specified date on
- nicer output

If you have any ideas on how to improve `activity journal` please let me know
or, preferably, create a pull request for improvements.
