#!/bin/sh

source venv/bin/activate
pg_ctl -D /usr/local/var/postgres start
python manage.py runserver
