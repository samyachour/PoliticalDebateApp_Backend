#!/bin/sh

deactivate
rm -rf venv
virtualenv --python=/usr/local/bin/python3  venv
source venv/bin/activate
brew link openssl # if this fails, follow the error's instructions to export the openssl paths
pip install -r requirements.txt
brew update
brew upgrade

# pip3 freeze > requirements.txt

# If you have problems with django finding the app folder
# echo "export PYTHONPATH="${PWD}/PoliticalDebateApp"" >> venv/bin/activate
