#!/bin/sh

ln rest_api/migrations/__init__.py ./
rm -rf rest_api/migrations
mkdir -p rest_api/migrations
mv __init__.py rest_api/migrations/

psql postgres -c "drop database PoliticalDebateApp;"
psql postgres -c "create database PoliticalDebateApp;"
psql postgres -c "grant all privileges on database PoliticalDebateApp to politicaldebateappowner;"
python manage.py makemigrations
python manage.py migrate
python manage.py test
python manage.py createsuperuser # use admin keychain account
python manage.py runserver
