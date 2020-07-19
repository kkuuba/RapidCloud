import time
from mega import Mega
from configuration_handler import get_mega_cloud_credentials


class MegaCloudInterface:

    def __init__(self, account_id=None):
        self.timestamp = time.time()
        self.account_id = account_id
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
        information = {"total_space": str(int(data["total"])),
                       "available_space": str(int(data["total"]) - int(data["used"]))
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

    def create_rapid_cloud_directory_if_not_exists(self):
        if not self.drive.find('RAPIDCLOUD'):
            self.drive.create_folder('RAPIDCLOUD')

    def authorization(self):
        mega = Mega()
        credentials = get_mega_cloud_credentials(self.account_id)
        self.drive = mega.login(credentials[0], credentials[1])
