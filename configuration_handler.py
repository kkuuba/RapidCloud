import json
from getpass import getpass


def get_data_from_json(account_id=None):
    with open("configuration.json", "r") as file:
        if account_id:
            for account in json.load(file)["cloud_providers"]:
                if account["account_id"] == account_id:
                    file.close()
                    return account
        else:
            data = json.load(file)
            file.close()
            return data


def put_data_in_json(data):
    with open("configuration.json", "w") as file:
        file.seek(0)
        json.dump(data, file)
        file.close()


def enter_new_account(provider):
    data = get_data_from_json()
    if data["cloud_providers"]:
        account_id = data["cloud_providers"][-1]["account_id"] + 1
    else:
        account_id = 1
        account_info = {
            "provider": provider,
            "account_id": account_id
        }
        data["cloud_providers"].append(account_info)

        put_data_in_json(data)
        print("Added new account")
    return account_id


def modify_account_parameter(account_id, parameter, value):
    data = get_data_from_json()
    for account in data["cloud_providers"]:
        if account["account_id"] == account_id:
            account[parameter] = value
    put_data_in_json(data)
    print("Parameter of account {} changed successfully".format(account_id))


def check_if_account_exist(account_id, provider):
    data = get_data_from_json()
    for account in data["cloud_providers"]:
        if account["account_id"] == account_id and account["provider"] == provider:
            return True
    else:
        return False


def get_mega_cloud_credentials(account_id):
    if check_if_account_exist(account_id, "megacloud"):
        data = get_data_from_json()
        for account in data["cloud_providers"]:
            if account["account_id"] == account_id:
                return account["mega_authorization"]["email"], account["mega_authorization"]["password"]
    else:
        print("Enter email to your Mega account:")
        email = input()
        print("Enter password to your Mega account:")
        password = getpass()
        data = get_data_from_json()
        if data["cloud_providers"]:
            account_id = data["cloud_providers"][-1]["account_id"] + 1
        else:
            account_id = 1
        account_info = {
            "provider": "megacloud",
            "account_id": account_id,
            "mega_authorization": {
                "email": email,
                "password": password
            }}
        data["cloud_providers"].append(account_info)
        put_data_in_json(data)
        print("Added new account")
        return email, password
