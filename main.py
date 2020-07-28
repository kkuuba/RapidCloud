from file_split_merge import SplitAndCombineFiles
from google_drive.gdrive import GoogleDriveInterface
from mega_drive.mdrive import MegaCloudInterface
from configuration_handler import ConfigurationHandler
import threading
import hashlib
import os
import re
import time


class RapidCloudTaskHandler(ConfigurationHandler):
    def __init__(self, path_to_task_object):
        self.path = path_to_task_object
        self.start = str(time.time())
        self.progress = None
        self.id = None
        self.provider = None
        self.tasks = []
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
        file_operation = SplitAndCombineFiles()
        os.popen("cp {} {}".format(self.path, "/tmp/"))
        new_name = self.generate_fragment_hash_string()
        os.popen("mv /tmp/{} /tmp/{}".format(file_name, new_name))
        time.sleep(3)
        divide_scheme = self.get_proper_file_divide_scheme()
        print(divide_scheme)
        file_operation.split("/tmp/{}".format(new_name), divide_scheme)
        self.upload_all_fragments(new_name)
        # self.delete_temp_files(new_name)

    def upload_all_fragments(self, new_filename):
        providers_data = self.get_data_from_json()
        for x in providers_data["cloud_providers"]:
            self.tasks.append(
                threading.Thread(
                    target=UnitDataTransferTask("{}-{}.ros".format(new_filename, x["account_id"]), x["account_id"],
                                                x["provider"]).export_fragment,
                    args=()))
            self.tasks[-1].daemon = True
            self.tasks[-1].start()

    @staticmethod
    def delete_temp_files(filename):
        pattern = re.compile(r"{}*.".format(filename))
        for root, dirs, files in os.walk("/tmp"):
            for file in filter(lambda x: re.match(pattern, x), files):
                os.remove(os.path.join(root, file))


class UnitDataTransferTask:
    def __init__(self, filename, provider_id, provider):
        self.filename = filename
        self.provider_id = provider_id
        self.provider_instance = self.recognize_provider(provider)

    def export_fragment(self):
        print("Starting export '{}' file".format(self.filename))
        self.provider_instance.upload_file(self.filename)
        print("'{}' exported with success".format(self.filename))

    def import_fragment(self):
        self.provider_instance.download_file(self.filename)

    def recognize_provider(self, provider):
        if provider == "google":
            return GoogleDriveInterface(self.provider_id)
        elif provider == "megacloud":
            return MegaCloudInterface(self.provider_id)


obj = RapidCloudTaskHandler("test_files/100MB.zip")
obj.export_file_to_cloud()

time.sleep(300)
