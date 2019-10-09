#!/bin/sh

ln rest_api/migrations/__init__.py ./
rm -rf rest_api/migrations
mkdir -p rest_api/migrations
mv __init__.py rest_api/migrations/

psql -c "drop database \"PoliticalDebateApp\";"
psql -c "create database \"PoliticalDebateApp\";"
python manage.py makemigrations
python manage.py migrate
python manage.py test
python manage.py createsuperuser # use default username w/ pass from secrets

# Run generate_database functions, server, and update stubs script
