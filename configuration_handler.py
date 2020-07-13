import json
from getpass import getpass


def enter_new_account(provider):
    with open("configuration.json", "r+") as file:
        data = json.load(file)
        if data["cloud_providers"]:
            account_id = data["cloud_providers"][-1]["account_id"] + 1
        else:
            account_id = 1
        account_info = {
            "provider": provider,
            "account_id": account_id
        }
        data["cloud_providers"].append(account_info)
        file.seek(0)
        json.dump(data, file)
        print("Added new account\n")
    return account_id


def modify_account_parameter(account_id, parameter, value):
    with open("configuration.json", "r+") as file:
        data = json.load(file)
        for account in data["cloud_providers"]:
            if account["account_id"] == account_id:
                account[parameter] = value
        file.seek(0)
        json.dump(data, file)
        print("Parameter of account {} changed successfully\n".format(account_id))


def check_if_account_exist(account_id, provider):
    with open("configuration.json", "r+") as file:
        data = json.load(file)
        for account in data["cloud_providers"]:
            if account["account_id"] == account_id and account["provider"] == provider:
                return True
        else:
            return False


def get_mega_cloud_credentials(account_id):
    if check_if_account_exist(account_id, "megacloud"):
        with open("configuration.json", "r+") as file:
            data = json.load(file)
            for account in data["cloud_providers"]:
                if account["account_id"] == account_id:
                    return account["mega_authorization"]["email"], account["mega_authorization"]["password"]
    else:
        print("Enter email to your Mega account:")
        email = input()
        print("Enter password to your Mega account:")
        password = getpass()
        with open("configuration.json", "r+") as file:
            data = json.load(file)
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
            file.seek(0)
            json.dump(data, file)
            print("Added new account\n")
        return email, password
