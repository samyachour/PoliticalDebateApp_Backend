# Shell script to create virtual environment

virtualenv --python=python3 venv
source venv/bin/activate
pip3 install Django
pip3 install djangorestframework
