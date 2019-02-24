# Shell script to create virtual environment

virtualenv --python=/usr/local/Cellar/python/3.7.2_2/bin/python3.7  venv
source venv/bin/activate
pip3 install Django
pip3 install djangorestframework
