import json
from getpass import getpass


class ConfigurationHandler:
    def __init__(self, account_identifier=None, provider=None):
        self.account_id = account_identifier
        self.provider = provider

    def get_data_from_json(self):
        with open("configuration.json", "r") as file:
            if self.account_id:
                for account in json.load(file)["cloud_providers"]:
                    if account["account_id"] == self.account_id:
                        file.close()
                        return account
            else:
                data = json.load(file)
                file.close()
                return data

    @staticmethod
    def put_data_in_json(data):
        with open("configuration.json", "w") as file:
            file.seek(0)
            json.dump(data, file)
            file.close()

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
        print("Added new account")
        return account_id

    def modify_account_parameter(self, parameter, value):
        data = self.get_data_from_json()
        for account in data["cloud_providers"]:
            if account["account_id"] == self.account_id:
                account[parameter] = value
        self.put_data_in_json(data)
        print("Parameter of account {} changed successfully".format(self.account_id))

    def check_if_account_exist(self):
        account = self.get_data_from_json()
        if account:
            return True
        else:
            return False

    def get_mega_cloud_credentials(self):
        if self.check_if_account_exist():
            account = self.get_data_from_json()
            if account["account_id"] == self.account_id:
                return account["mega_authorization"]["email"], account["mega_authorization"]["password"]
        else:
            print("Enter email to your Mega account:")
            email = input()
            print("Enter password to your Mega account:")
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
            print("Added new account")
            return email, password
