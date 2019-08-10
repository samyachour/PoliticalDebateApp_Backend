from pip._internal import main
import json
import pprint
import fileinput

try:
    import requests
except ImportError:
    main(['install', 'requests'])
    import requests

def convertToDoubleQuotes(filename):
    with fileinput.FileInput(filename, inplace=True) as file:
        for line in file:
            # Correct JSON
            line = line.replace("None", "null")
            print(line.replace("'", '"'), end='')

version = 'v1/'
baseURL = 'http://localhost:8000/api/' + version

# AUTH

username = "reservedstubgenerationacct@mail.com"
password = "testing"

url = baseURL + 'auth/token/obtain/'
body = {"username": username, "password": password}
response = requests.post(url, json=body)
response.raise_for_status() # ensure we notice bad responses

file = open("TokenObtain.json", "w")
serialized_response = json.loads(response.text.replace("'", '"'))
pprint.pprint(serialized_response, file)
file.close()
convertToDoubleQuotes(file.name)


access_token = serialized_response["access"]
refresh_token = serialized_response["refresh"]

url = baseURL + 'auth/token/refresh/'
body = { "refresh": refresh_token }
response = requests.post(url, json=body)
response.raise_for_status()

file = open("TokenRefresh.json", "w")
serialized_response = json.loads(response.text)
pprint.pprint(serialized_response, file)
file.close()
convertToDoubleQuotes(file.name)



# DEBATES

url = baseURL + 'debate/search/'
response = requests.post(url)
response.raise_for_status()

file = open("DebateSearch.json", "w")
serialized_response = json.loads(response.text) # from above response
pprint.pprint(serialized_response, file)
file.close()
convertToDoubleQuotes(file.name)


url = baseURL + 'debate/1'
response = requests.get(url)
response.raise_for_status()

file = open("DebateSingle.json", "w")
serialized_response = json.loads(response.text)
pprint.pprint(serialized_response, file)
file.close()
convertToDoubleQuotes(file.name)



# PROGRESS

headers = {"Authorization": "Bearer {0}".format(access_token)}

url = baseURL + 'progress/'
response = requests.get(url, headers=headers)
response.raise_for_status()

file = open("ProgressAll.json", "w")
serialized_response = json.loads(response.text)
pprint.pprint(serialized_response, file)
file.close()
convertToDoubleQuotes(file.name)


url = baseURL + 'progress/1'
response = requests.get(url, headers=headers)
response.raise_for_status()

file = open("ProgressSingle.json", "w")
serialized_response = json.loads(response.text)
pprint.pprint(serialized_response, file)
file.close()
convertToDoubleQuotes(file.name)



# STARRED

url = baseURL + 'starred/'
response = requests.get(url, headers=headers)
response.raise_for_status()

file = open("Starred.json", "w")
serialized_response = json.loads(response.text)
pprint.pprint(serialized_response, file)
file.close()
convertToDoubleQuotes(file.name)
