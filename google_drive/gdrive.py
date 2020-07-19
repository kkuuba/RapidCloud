import time
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from configuration_handler import enter_new_account, check_if_account_exist


class GoogleDriveInterface:

    def __init__(self, account_id=None):
        self.timestamp = time.time()
        self.account_id = account_id
        self.drive_auth = GoogleAuth()
        self.authorization()
        self.drive = GoogleDrive(self.drive_auth)
        self.rapid_cloud_directory_id = self.get_rapid_cloud_directory_id()

    def upload_file(self, filename=None):
        file_to_upload = self.drive.CreateFile({'parents': [{'id': self.rapid_cloud_directory_id}], "title": filename})
        file_to_upload.SetContentFile("/tmp/{}".format(filename))
        file_to_upload.Upload()

    def download_file(self, filename=None):
        file_to_download = self.drive.CreateFile({'id': self.get_info_about_file(filename)["file_id"]})
        file_to_download.GetContentFile("/tmp/{}".format(filename))

    def get_cloud_provider_data(self):
        data = self.drive.GetAbout()
        information = {"total_space": data["quotaBytesTotal"],
                       "available_space": str(int(data["quotaBytesTotal"]) - int(data["quotaBytesUsedAggregate"]))
                       }
        return information

    def get_info_about_file(self, filename):
        data = self.drive.ListFile({'q': "title = '{}'".format(filename), 'spaces': 'drive'}).GetList()
        if data:
            try:
                information = {"size": data[0]["fileSize"],
                               "file_id": data[0]["id"],
                               "owner_email": data[0]["owners"][0]["emailAddress"]
                               }
            except KeyError:
                information = {"file_id": data[0]["id"],
                               "owner_email": data[0]["owners"][0]["emailAddress"]
                               }
            return information
        else:
            return None

    def get_rapid_cloud_directory_id(self):
        if self.get_info_about_file("RAPIDCLOUD"):
            return self.get_info_about_file("RAPIDCLOUD")["file_id"]
        else:
            folder_metadata = {'title': 'RAPIDCLOUD', 'mimeType': 'application/vnd.google-apps.folder'}
            folder = self.drive.CreateFile(folder_metadata)
            folder.Upload()
            return self.get_info_about_file("RAPIDCLOUD")["file_id"]

    def authorization(self):
        if check_if_account_exist(self.account_id, "google"):
            self.drive_auth.LoadCredentialsFile("google_drive/mycreds_{}.txt".format(self.account_id))
        if self.drive_auth.credentials is None:
            self.drive_auth.LocalWebserverAuth()
            self.account_id = enter_new_account("google")
        elif self.drive_auth.access_token_expired:
            print("Refreshing api token ...")
            self.drive_auth.Refresh()
        else:
            self.drive_auth.Authorize()
        self.drive_auth.SaveCredentialsFile("google_drive/mycreds_{}.txt".format(self.account_id))
