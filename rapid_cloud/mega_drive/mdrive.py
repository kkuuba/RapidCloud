import time
from mega import Mega
from rapid_cloud.configuration_handler import ConfigurationHandler


class MegaCloudInterface(ConfigurationHandler):

    def __init__(self, account_id=None):
        super().__init__(account_id, "megacloud")
        self.timestamp = time.time()
        self.drive = None
        self.authorization()
        self.create_rapid_cloud_directory_if_not_exists()

    def upload_file(self, filename=None):
        folder = self.drive.find('RAPIDCLOUD')
        self.drive.upload("/tmp/{}".format(filename), folder[0], filename)

    def download_file(self, filename=None):
        file_to_download = self.drive.find(filename)
        self.drive.download(file_to_download, "/tmp")

    def get_cloud_provider_data(self):
        data = self.drive.get_storage_space(kilo=True)
        information = {"total_space": str(round(int(data["total"]) / 1073741824, 4)),
                       "used_space": str(round(int(data["used"]) / 1073741824, 4)),
                       "available_space": str(round((int(data["total"]) - int(data["used"])) / 1073741824, 4)),
                       "email": data["email"]
                       }
        return information

    def get_info_about_file(self, filename):
        data = self.drive.find(filename)
        user_data = self.drive.get_user()
        if data and user_data:
            try:
                information = {"size": data[1]["s"],
                               "file_id": data[1]["h"],
                               "owner_email": user_data["email"]
                               }
            except KeyError:
                information = {"file_id": data[1]["h"],
                               "owner_email": user_data["email"]
                               }
            return information
        else:
            return None

    def delete_file(self, filename):
        file = self.drive.find(filename)
        self.drive.delete(file[0])
        self.drive.empty_trash()

    def create_rapid_cloud_directory_if_not_exists(self):
        if not self.drive.find('RAPIDCLOUD'):
            self.drive.create_folder('RAPIDCLOUD')

    def authorization(self):
        mega = Mega()
        credentials = self.get_mega_cloud_credentials()
        self.drive = mega.login(credentials[0], credentials[1])
