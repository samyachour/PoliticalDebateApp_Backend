#!/bin/sh

virtualenv --python=/usr/local/bin/python3  venv
source venv/bin/activate
pip3 install Django
pip3 install djangorestframework
pip3 install djangorestframework_simplejwt
brew link openssl # if this fails, follow the error's instructions to export the openssl paths
pip3 install psycopg2
brew update
brew upgrade

# If you have problems with django finding the app folder
# echo "export PYTHONPATH="${PWD}/PoliticalDebateApp"" >> venv/bin/activate
