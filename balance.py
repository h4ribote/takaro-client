import requests
import json

api_token = input("api_token: ")

response = requests.post('http://tak-api.h4ribote.net/balance.php', data={'api_token': api_token})

data = (response.text)

data = json.loads(data)

if ('error' in data):
    print(data['error'])
else:
    for data2 in data:
        print(data2['amount']+data2['unit']+"\n")

input("press enter to exit")
