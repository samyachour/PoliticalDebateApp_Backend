# Shell script to create virtual environment

virtualenv --python=/usr/local/Cellar/python/3.7.2_2/bin/python3.7  venv
source venv/bin/activate
pip3 install Django
pip3 install djangorestframework
pip3 install psycopg2
pip3 install psycopg2-binary
brew update
brew upgrade

# If you have problems with django finding the app folder
# echo "export PYTHONPATH="${PWD}/PoliticalDebateApp"" >> venv/bin/activate
