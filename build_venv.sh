#!/bin/sh

deactivate
rm -rf venv
virtualenv --python=/usr/local/bin/python3  venv
source venv/bin/activate
pip3 install Django
pip3 install djangorestframework
pip3 install djangorestframework_simplejwt
brew link openssl # if this fails, follow the error's instructions to export the openssl paths
pip3 install psycopg2
pip3 install gunicorn
pip3 install django-heroku
pip3 install dj-database-url
pip3 install whitenoise
pip3 install PyGithub
brew update
brew upgrade

export DEBUG=True
export THROTTLE=False

# pip3 freeze > requirements.txt

# If you have problems with django finding the app folder
# echo "export PYTHONPATH="${PWD}/PoliticalDebateApp"" >> venv/bin/activate
