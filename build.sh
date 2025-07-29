#!/usr/bin/env bash
# exit on error
set -o errexit

# The commands below are run by Render to build your app
pip install -r requirements.txt

flask db init
flask db migrate -m "Initial migration."
flask db upgrade