import requests
import json
import hashlib
import multiprocessing

variable = {}
checked = 0

domain = "http://tak-api.h4ribote.net/"
class Color:
	RED            = '\033[31m'
	GREEN          = '\033[32m'
	YELLOW         = '\033[33m'
	BLUE           = '\033[34m'
	MAGENTA        = '\033[35m'
	CYAN           = '\033[36m'
	WHITE          = '\033[37m'
	COLOR_DEFAULT  = '\033[39m'
	BOLD           = '\033[1m'


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
        print(f"\n{Color.RED}error: {data['error']}{Color.COLOR_DEFAULT}")
    else:
        print(f"\n送金が完了しました\n送金ID: {str(data['transfer_id'])}\n時間: {str(data['time'])}\n出金元: {str(data['source'])}\n送金先: {str(data['dest'])}\n金額: {str(data['amount'])}{str(data['unit'])}\nコメント: {str(data['comment'])}")


def balance(variable):
    api_token = variable['api_token']

    response = requests.post(domain + 'balance.php', data={'api_token': api_token})

    data = (response.text)

    data = json.loads(data)

    if ('error' in data):
        print(f"\n{Color.RED}error: {data['error']}{Color.COLOR_DEFAULT}")
    else:
        for data2 in data:
            print(f"{Color.YELLOW}{data2['amount']}{Color.COLOR_DEFAULT}{data2['unit']}\n")


def find_nonce(previous_hash, target_prefix_zeros, start_nonce, end_nonce, result_queue):
    global variable
    global checked

    nonce = start_nonce
    while nonce < end_nonce:
        data = f"{previous_hash}{nonce}"
        hash_result = hashlib.sha256(data.encode('utf-8')).hexdigest()
        if hash_result.startswith('0' * target_prefix_zeros):
            result_queue.put(nonce)
            return
        nonce += 1
        checked += 1
    result_queue.put(None)

def parallel_find_nonce(previous_hash, target_prefix_zeros, num_processes=2):
    global variable
    result_queue = multiprocessing.Queue()
    processes = []
    nonce_range = 2**32 // num_processes

    for i in range(num_processes):
        start_nonce = i * nonce_range
        end_nonce = (i + 1) * nonce_range if i != num_processes - 1 else 2**32
        process = multiprocessing.Process(target=find_nonce, args=(previous_hash, target_prefix_zeros, start_nonce, end_nonce, result_queue))
        processes.append(process)
        process.start()

    for process in processes:
        process.join()

    while not result_queue.empty():
        result = result_queue.get()
        if result is not None:
            return result

    return None

def mine_tak(api_token,num_processe):
    api_token = variable['api_token']

    response = requests.post(domain + 'mining/task.php')

    data = json.loads(response.text)

    if ('error' in data):
        print(f"\n{Color.RED}error: {data['error']}{Color.COLOR_DEFAULT}")
    else:
        for data_ in data:
            task_id = data_['id']
            task_data = data_['data']
            difficulty = data_['difficulty']
            reward_amount = data_['reward']
            reward_unit = data_['reward_unit']
            mined = int(data_['mined'])

    if mined == 1:
        return(f"{Color.RED}error: there are no mining tasks{Color.COLOR_DEFAULT}")
    
    print(f"{Color.CYAN}<--- Task found --->{Color.COLOR_DEFAULT}\ntask_id: {Color.YELLOW}{task_id}{Color.COLOR_DEFAULT} difficulty: {Color.YELLOW}{difficulty}{Color.COLOR_DEFAULT}\nreward: {Color.YELLOW}{reward_amount}{reward_unit}{Color.COLOR_DEFAULT}\n")

    print("Starting mining process...\n")

    found_nonce = parallel_find_nonce(task_data, difficulty, num_processe)

    response2 = requests.post(domain + 'mining/verification.php', data={'nonce':found_nonce, 'api_token': api_token})
    data2 = json.loads(response2.text)

    if ('error' in data2):
        return(f"\n{Color.RED}error: {data['error']}{Color.COLOR_DEFAULT}")

    else:
        for data2_ in data2:
            task_id = data2_['id']
            reward = (f"{data2_['reward']}{data2_['reward_unit']}")
        return(f"{Color.GREEN}マイニングに成功しました{Color.COLOR_DEFAULT}\nタスクID: {task_id}\n報酬: {reward}")

def main():
    global variable
    if not 'api_token' in variable:
        variable['api_token'] = input("api_token: ")
    while True:
        command = input("$ ")

        if command:
            print("")

        if command == "transfer":
            transfer(variable)

        elif command == "balance":
            balance(variable)

        elif command == "help":
            print("balance\n  残高を表示\ntransfer\n  送金\nmine [プロセス数(デフォルトは2)]\n  takaroのマイニング\nset [変数名]\n  変数を設定\nshow [変数名]\n  変数の値を取得")

        elif command.startswith("set "):
            set_variable = command[4:]
            variable[set_variable] = input(f"{set_variable}:")

        elif command.startswith("show "):
            show_value = command[5:]
            print(variable.get(show_value, 'variable not found'))

        elif command.startswith("mine"):
            if len(command) > 5 :
                process_num = command[5:]
                try:
                    print(mine_tak(variable['api_token'],int(process_num)))
                except:
                    print(f"{Color.RED}error: プロセス数は整数で指定してください{Color.COLOR_DEFAULT}")
            else:
                print(mine_tak(variable['api_token'],2))

        elif command == "exit":
            return

        elif command:
            print("command not found")

        if command:
            print("\n")

        command = ""


if __name__ == '__main__':
    multiprocessing.freeze_support()

    main()
