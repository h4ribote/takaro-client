import requests
import json

api_token = input("api_token: ")
dest_user = input("dest_user: ")
unit = input("unit: ")
amount = input("amount: ")
comment = input("comment: ")

response = requests.post('http://tak-api.h4ribote.net/transfer.php', data={'api_token': api_token,'dest': dest_user,'unit': unit,'amount': amount,'comment': comment})

data = (response.text)

data = json.loads(data)


if ('error' in data):
    print("\n" + data['error'])
else:
    print(f"\n送金が完了しました\n送金ID: {str(data['transfer_id'])}\n時間: {str(data['time'])}\n出金元: {str(data['source'])}\n送金先: {str(data['dest'])}\n金額: {str(data['amount'])}{str(data['unit'])}\nコメント: {str(data['comment'])}")

input("press enter to exit")