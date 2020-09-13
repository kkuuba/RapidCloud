from google_drive.gdrive import GoogleDriveInterface
from mega_drive.mdrive import MegaCloudInterface
from configuration_handler import ConfigurationHandler
from getpass import getpass, getuser
from zipfile import ZipFile
from os.path import basename
import pyAesCrypt
import threading
import os
import re
import json
import shutil
import time

user_name = getuser()


class UnitDataTransferTask:
    def __init__(self, filename, provider_id, provider):
        self.filename = filename
        self.provider_id = provider_id
        self.provider_instance = self.recognize_provider(provider)
        self.finish = False
        self.start_time = time.time()
        self.transfer_duration = 0

    def export_fragment(self):
        print("Starting export '{}' file".format(self.filename))
        self.provider_instance.upload_file(self.filename)
        print("File '{}' exported with success".format(self.filename))
        self.transfer_duration = time.time() - self.start_time
        self.finish = True

    def import_fragment(self):
        print("Starting import of '{}' file".format(self.filename))
        self.provider_instance.download_file(self.filename)
        print("File '{}' imported with success".format(self.filename))
        self.transfer_duration = time.time() - self.start_time
        self.finish = True

    def recognize_provider(self, provider):
        if provider == "google":
            return GoogleDriveInterface(self.provider_id)
        elif provider == "megacloud":
            return MegaCloudInterface(self.provider_id)


class ThroughputTest:
    def __init__(self, account_id):
        self.configuration_handler = ConfigurationHandler(account_id)
        self.account_id = account_id
        self.provider = self.create_cloud_provider_instance()
        self.up_link_speed = None

    def create_cloud_provider_instance(self):
        return self.configuration_handler.get_data_from_json()["provider"]

    @staticmethod
    def delete_test_files():
        pattern = re.compile(r"{}*.".format("test"))
        for root, dirs, files in os.walk("/tmp"):
            for file in filter(lambda x: re.match(pattern, x), files):
                os.remove(os.path.join(root, file))

    def up_link_sub_test(self, sub_test_id, tp=14):
        subtest_start = time.time()
        subtest_result = {}
        start_data_size = 2
        while True:
            start_data_size = start_data_size * 2
            test_file_name = "test_{}_{}K".format(str(sub_test_id), str(start_data_size))
            with open("/tmp/{}".format(test_file_name), 'wb') as file_1:
                file_1.write(os.urandom(1024 * start_data_size))
                file_1.close()
            transfer_task = UnitDataTransferTask(test_file_name, self.account_id, self.provider)
            transfer_task.export_fragment()
            subtest_result.update({test_file_name: 1024 * start_data_size / transfer_task.transfer_duration})
            if time.time() - subtest_start > tp:
                break
        self.up_link_speed = sum(subtest_result.values()) / len(subtest_result.keys())


class FileEncryption:
    def __init__(self, file_name, password):
        self.file_name = file_name
        self.password = password
        self.ciphering = pyAesCrypt
        self.buffer_size = 64 * 1024

    def encryption(self):
        self.ciphering.encryptFile(self.file_name, "/tmp/{}".format(self.file_name + ".aes"), self.password,
                                   self.buffer_size)

    def decryption(self):
        self.ciphering.decryptFile("/tmp/{}".format(self.file_name), self.file_name.replace(".aes", ""), self.password,
                                   self.buffer_size)

    def zip_file(self):
        with ZipFile("/tmp/{}.zip".format(self.file_name.split(".")[0]), 'w') as zip_archive:
            path = "/tmp/{}.aes".format(self.file_name)
            zip_archive.write(path, basename(path))
        print('File zipped successfully!')

    def unzip_file(self):
        with ZipFile("/tmp/{}".format(self.file_name), 'r') as zip_archive:
            self.file_name = zip_archive.namelist()[0]
            zip_archive.extractall("/tmp/")
        print('Extracting all the files now...')

    def prepare_file_to_export(self):
        self.encryption()
        self.zip_file()

    def prepare_file_after_import(self):
        self.unzip_file()
        self.decryption()


def log(value):
    """ This is just a print method"""
    print(value)


def check_provider_performance(provider_id, n=3):
    account_config = ConfigurationHandler(provider_id)
    tasks = []
    threads = []
    for k in range(n):
        tasks.append(ThroughputTest(provider_id))
        threads.append(threading.Thread(target=tasks[-1].up_link_sub_test, args=[k]))
        threads[-1].daemon = True
        threads[-1].start()
    time.sleep(20)
    account_config.modify_account_parameter("up_link", sum(test.up_link_speed for test in tasks) / n)
    ThroughputTest.delete_test_files()


def check_performance():
    configuration_handler = ConfigurationHandler()
    info = configuration_handler.get_data_from_json()
    for account in info["cloud_providers"]:
        check_provider_performance(account["account_id"])


def check_if_providers_defined():
    try:
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
    os.mkdir(path="/home/{}/.config/rapid_cloud_data".format(user_name))
    os.mkdir(path="/home/{}/.config/rapid_cloud_data/exported_files".format(user_name))
    os.mkdir(path="/home/{}/.config/rapid_cloud_data/google_drive".format(user_name))
    with open("/home/{}/.config/rapid_cloud_data/configuration.json".format(user_name), "w+") as file:
        file.write("""{"cloud_providers": [], "password": ""}""")
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
        setup_password()
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
        check_performance()


def setup_password():
    log("Enter new password for your rapid_cloud app:")
    password = getpass()
    log("Enter password again:")
    password_repeated = getpass()
    if password == password_repeated:
        log("New password setup with success")
        data = json.load(open("/home/{}/.config/rapid_cloud_data/configuration.json".format(user_name), "r"))
        data["password"] = password
        with open("/home/{}/.config/rapid_cloud_data/configuration.json".format(user_name), "w") as file:
            file.seek(0)
            json.dump(data, file)
            file.close()
    else:
        log("Password did not match!")


def reset_configuration():
    shutil.rmtree("/home/{}/.config/rapid_cloud_data".format(user_name))
    log("Configuration was successfully removed")


def show_cloud_files():
    exported_files = os.listdir("/home/{}/.config/rapid_cloud_data/exported_files".format(user_name))
    for file in exported_files:
        log(file)


def show_cloud_parameters():
    log("Not implemented yet")
