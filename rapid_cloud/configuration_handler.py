import os
import json
import logging
from getpass import getpass, getuser


class ConfigurationHandler:
    def __init__(self, account_identifier=None, provider=None):
        self.account_id = account_identifier
        self.provider = provider
        self.user_name = getuser()

    def get_data_from_json(self):
        with open("/home/{}/.config/rapid_cloud_data/configuration.json".format(self.user_name), "r") as file:
            if self.account_id:
                for account in json.load(file)["cloud_providers"]:
                    if account["account_id"] == self.account_id:
                        file.close()
                        return account
            else:
                data = json.load(file)
                file.close()
                return data

    def put_data_in_json(self, data):
        with open("/home/{}/.config/rapid_cloud_data/configuration.json".format(self.user_name), "w") as file:
            file.seek(0)
            json.dump(data, file)
            file.close()

    def get_rapid_cloud_password(self):
        with open("/home/{}/.config/rapid_cloud_data/configuration.json".format(self.user_name), "r") as file:
            file.seek(0)
            password = json.load(file)["password"]
            file.close()
            return password

    def enter_new_account(self):
        data = self.get_data_from_json()
        if data["cloud_providers"]:
            account_id = data["cloud_providers"][-1]["account_id"] + 1
        else:
            account_id = 1
        account_info = {
            "provider": self.provider,
            "account_id": account_id
        }
        data["cloud_providers"].append(account_info)

        self.put_data_in_json(data)
        log_to_file("Added new account")
        return account_id

    def modify_account_parameter(self, parameter, value):
        data = json.load(open("/home/{}/.config/rapid_cloud_data/configuration.json".format(self.user_name), "r"))
        for account in data["cloud_providers"]:
            if account["account_id"] == self.account_id:
                account[parameter] = value
        self.put_data_in_json(data)
        log_to_file("Parameter of account {} changed successfully".format(self.account_id))

    def check_if_account_exist(self):
        if self.account_id:
            return True
        else:
            return False

    def get_mega_cloud_credentials(self):
        if self.check_if_account_exist():
            account = self.get_data_from_json()
            if account["account_id"] == self.account_id:
                return account["mega_authorization"]["email"], account["mega_authorization"]["password"]
        else:
            log_to_console("Enter email to your Mega account:")
            email = input()
            log_to_console("Enter password to your Mega account:")
            password = getpass()
            data = self.get_data_from_json()
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
            self.put_data_in_json(data)
            log_to_console("Added new account")
            return email, password


def log_to_console(value):
    print(value)


def log_to_file(value):
    logging.info(value)


def setup_log_file():
    logging.basicConfig(filename="/home/{}/.config/rapid_cloud_data/debug.log".format(getuser()), level=logging.DEBUG)


def create_directory(dir_path):
    try:
        os.mkdir(path=dir_path)
    except OSError:
        pass
