from google_drive.gdrive import GoogleDriveInterface
from mega_drive.mdrive import MegaCloudInterface
from zipfile import ZipFile
from os.path import basename
import pyAesCrypt
import os
import json
from getpass import getpass, getuser
import shutil

user_name = getuser()


class UnitDataTransferTask:
    def __init__(self, filename, provider_id, provider):
        self.filename = filename
        self.provider_id = provider_id
        self.provider_instance = self.recognize_provider(provider)
        self.finish = False

    def export_fragment(self):
        print("Starting export '{}' file".format(self.filename))
        self.provider_instance.upload_file(self.filename)
        print("File '{}' exported with success".format(self.filename))
        self.finish = True

    def import_fragment(self):
        print("Starting import of '{}' file".format(self.filename))
        self.provider_instance.download_file(self.filename)
        print("File '{}' imported with success".format(self.filename))
        self.finish = True

    def recognize_provider(self, provider):
        if provider == "google":
            return GoogleDriveInterface(self.provider_id)
        elif provider == "megacloud":
            return MegaCloudInterface(self.provider_id)


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
