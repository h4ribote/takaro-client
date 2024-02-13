import requests
import json
import hashlib
import multiprocessing
import time

variable = {}

domain = "http://tak-api.h4ribote.net/"


def transfer(variable):
    api_token = variable['api_token']
    dest_user = input("dest_user: ")
    unit = input("unit: ")
    amount = input("amount: ")
    comment = input("comment: ")

    response = requests.post(domain + 'transfer.php', data={'api_token': api_token,'dest': dest_user,'unit': unit,'amount': amount,'comment': comment})

    data = (response.text)

    data = json.loads(data)


    if ('error' in data):
        print("\n" + data['error'])
    else:
        print(f"\n送金が完了しました\n送金ID: {str(data['transfer_id'])}\n時間: {str(data['time'])}\n出金元: {str(data['source'])}\n送金先: {str(data['dest'])}\n金額: {str(data['amount'])}{str(data['unit'])}\nコメント: {str(data['comment'])}")


def balance(variable):
    api_token = variable['api_token']

    response = requests.post(domain + 'balance.php', data={'api_token': api_token})

    data = (response.text)

    data = json.loads(data)

    if ('error' in data):
        print(data['error'])
    else:
        for data2 in data:
            print(data2['amount']+data2['unit']+"\n")


def find_nonce(task_data, difficulty):
    start_time = time.perf_counter()
    nonce = 0
    calculated = 0
    while True:
        data = f"{task_data}{nonce}"
        hash_result = hashlib.sha256(data.encode('utf-8')).hexdigest()
        current_time = time.perf_counter()
        passed = round(current_time - start_time,1)
        try:
            hash_rate = round(calculated/passed,2)
        except:
            hash_rate = 0
        print(f"\r{nonce}  経過:{passed}s ハッシュレート:{hash_rate}h/s",end="")
        if hash_result.startswith('0' * difficulty):
            return nonce
        calculated += 1
        nonce += 1


def mine_tak(variable):
    api_token = variable['api_token']

    response = requests.post(domain + 'mining/task.php')

    data = (response.text)

    data = json.loads(data)

    if ('error' in data):
        return("\nerror:" + data['error'])
    else:
        for data_ in data:
            task_data = data_['data']
            difficulty = data_['difficulty']
            mined = int(data_['mined'])

    if mined == 1:
        return("error:there are no mining tasks")

    found_nonce = find_nonce(task_data, difficulty)

    response2 = requests.post(domain + 'mining/verification.php', data={'nonce':found_nonce, 'api_token': api_token})
    data2 = (response2.text)
    data2 = json.loads(data2)


    if ('error' in data2):
        for data2_ in data2:
            return(f"\nerror:{data2['error']}")

    else:
        for data2_ in data2:
            task_id = data2_['id']
            reward = (f"{data2_['reward']}{data2_['reward_unit']}")
        return(f"\nマイニングに成功しました\nタスクID: {task_id}\n報酬: {reward}")

def main():
    global variable
    variable['api_token'] = input("api_token:")
    while True:
        command = input("$ ")
        if command:
            print("")
        if command == "transfer":
            transfer(variable)
        elif command == "balance":
            balance(variable)
        elif command == "mine":
            print(mine_tak(variable))
        elif command == "help":
            print("balance\n  残高を表示\ntransfer\n  送金\nmine [プロセス数(デフォルトは2)]\n  takaroのマイニング\nset [変数名]\n  変数を設定\nshow [変数名]\n  変数の値を取得")
        elif command.startswith("set "):
            set_variable = command[4:]
            variable[set_variable] = input(f"{set_variable}:")
        elif command.startswith("show "):
            show_value = command[5:]
            print(variable.get(show_value, 'variable not found'))
        elif command == "exit":
            return
        elif command:
            print("command not found")
        if command:
            print("\n")
        command = ""


if __name__ == '__main__':
    main()