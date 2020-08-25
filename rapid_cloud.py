from file_split_merge import SplitAndCombineFiles
from google_drive.gdrive import GoogleDriveInterface
from mega_drive.mdrive import MegaCloudInterface
from configuration_handler import ConfigurationHandler
from utilities import UnitDataTransferTask, FileEncryption
import argparse
import threading
import hashlib
import os
import re
import time
import json
import getpass


class RapidCloudTaskHandler(ConfigurationHandler):
    def __init__(self, path_to_task_object, password):
        self.file_operation = SplitAndCombineFiles()
        self.encryption_key = password
        self.file_encryption = FileEncryption(path_to_task_object, self.encryption_key)
        self.path = path_to_task_object
        self.start = str(time.time())
        self.progress = None
        self.id = None
        self.provider = None
        self.tasks = []
        self.threads = []
        self.transfer_finished = False
        self.file_trace = {}
        super().__init__()

    def get_proper_file_divide_scheme(self):
        """
        Here will be code to obtain file spliting

        :return:
        """
        providers_count = len(self.get_data_from_json()["cloud_providers"])
        if providers_count == 0:
            GoogleDriveInterface()
            MegaCloudInterface()
        return str(len(self.get_data_from_json()["cloud_providers"]))

    def generate_fragment_hash_string(self):
        return str(hashlib.sha256(self.start.encode("utf-8")).hexdigest())

    def export_file_to_cloud(self):
        file_name = self.path.split("/")[-1]
        self.file_encryption.prepare_file_to_export()
        new_name = self.generate_fragment_hash_string()
        os.popen("mv /tmp/{} /tmp/{}".format("{}.zip".format(file_name.split(".")[0]), new_name))
        time.sleep(3)
        divide_scheme = self.get_proper_file_divide_scheme()
        print(divide_scheme)
        self.file_operation.split("/tmp/{}".format(new_name), divide_scheme)
        self.upload_all_fragments(new_name)
        self.wait_for_transfer_off_all_fragments()
        self.delete_temp_files(new_name)
        self.delete_temp_files("aes")
        self.create_original_file_trace(file_name)

    def create_original_file_trace(self, original_file_name):
        file = open("{}.rp".format(original_file_name.split(".")[0]), "w")
        file.write(json.dumps(self.file_trace))
        file.close()

    def import_file_from_cloud(self):
        file = open(self.path, mode='r')
        self.file_trace = json.loads(file.read())
        keys_list = list(self.file_trace.keys())
        for key in keys_list:
            self.tasks.append(
                UnitDataTransferTask(key, self.file_trace[key]["account_id"], self.file_trace[key]["provider"]))
            self.threads.append(threading.Thread(target=self.tasks[-1].import_fragment, args=()))
            self.threads[-1].daemon = True
            self.threads[-1].start()
        self.wait_for_transfer_off_all_fragments()
        hash_name = keys_list[-1].split("-")[0]
        self.file_operation.merge("/tmp/{}.zip".format(keys_list[-1]).split("-")[0])
        self.file_encryption = FileEncryption(hash_name, self.encryption_key)
        self.file_encryption.prepare_file_after_import()
        self.delete_temp_files(hash_name)
        self.delete_temp_files("aes")

    def wait_for_transfer_off_all_fragments(self):
        while True:
            self.transfer_finished = True
            for task in self.tasks:
                if not task.finish:
                    self.transfer_finished = False
                    break
            if self.transfer_finished:
                break
            time.sleep(2)

    def upload_all_fragments(self, new_filename):
        providers_data = self.get_data_from_json()
        UnitDataTransferTask("{}-{}.ros".format(new_filename, "CRC"), 1,
                             providers_data["cloud_providers"][0]["provider"]).export_fragment()
        self.file_trace.update({
            "{}-{}.ros".format(new_filename, "CRC"): providers_data["cloud_providers"][0]
        })
        for x in providers_data["cloud_providers"]:
            self.file_trace.update({
                "{}-{}.ros".format(new_filename, x["account_id"]): x
            })
            self.tasks.append(UnitDataTransferTask("{}-{}.ros".format(new_filename, x["account_id"]), x["account_id"],
                                                   x["provider"]))
            self.threads.append(threading.Thread(target=self.tasks[-1].export_fragment, args=()))
            self.threads[-1].daemon = True
            self.threads[-1].start()

    @staticmethod
    def delete_temp_files(filename):
        pattern = re.compile(r"{}*.".format(filename))
        for root, dirs, files in os.walk("/tmp"):
            for file in filter(lambda x: re.match(pattern, x), files):
                os.remove(os.path.join(root, file))


def log(value):
    """ This is just a print method"""
    print(value)


def check_if_providers_defined():
    try:
        user_name = getpass.getuser()
        with open("/home/{}/.config/rapid_cloud_data/configuration.json".format(user_name), "r") as file:
            data = json.load(file)
            file.close()
        if data["cloud_providers"]:
            return True
        else:
            return False
    except FileNotFoundError:
        return False


def set_default_configuration_scheme():
    user_name = getpass.getuser()
    os.mkdir(path="/home/{}/.config/rapid_cloud_data".format(user_name))
    os.mkdir(path="/home/{}/.config/rapid_cloud_data/google_drive".format(user_name))
    with open("/home/{}/.config/rapid_cloud_data/configuration.json".format(user_name), "w+") as file:
        file.write("""{"cloud_providers": []}""")
        file.close()
    with open("/home/{}/.config/rapid_cloud_data/google_drive/client_secrets.json".format(user_name), "w+") as file:
        file.write(
            """{"installed": {"client_id": "894311503588-qi4p4ld3fng02a0c8j0mfvk656a4698t.apps.googleusercontent.com",
                               "project_id": "quickstart-1583352235400",
                               "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                               "token_uri": "https://oauth2.googleapis.com/token",
                               "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                               "client_secret": "hSJvUATRj3p-s7bY1iXxZWkm",
                               "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"]}}"""
        )
        file.close()


def prepare_all_accounts():
    if not check_if_providers_defined():
        set_default_configuration_scheme()
        while True:
            log("Please enter cloud provider name [google, megacloud]:")
            provider = str(input())
            if provider == "google":
                GoogleDriveInterface()
            elif provider == "megacloud":
                MegaCloudInterface()
            else:
                log("Unknown provider\n")
                continue
            log("Do you want to add another account? [yes/no]")
            end_preparation = str(input()) == "no"
            if end_preparation:
                break


def main():
    try:
        parser = argparse.ArgumentParser(description='Export or import file to cloud storage')
        parser.add_argument('filename')
        prepare_all_accounts()
        args = parser.parse_args()
        is_valid_file = os.path.exists(args.filename)
        if args.filename.split(".")[-1] == "rp" and is_valid_file:
            transfer_obj = RapidCloudTaskHandler(args.filename, password="secret")
            transfer_obj.import_file_from_cloud()

        elif args.filename and is_valid_file:
            transfer_obj = RapidCloudTaskHandler(args.filename, password="secret")
            transfer_obj.export_file_to_cloud()

        else:
            log("No proper file provided")
    except KeyboardInterrupt:
        log("Execution interrupted\n")
        exit()


if __name__ == "__main__":
    main()
