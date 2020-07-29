from file_split_merge import SplitAndCombineFiles
from google_drive.gdrive import GoogleDriveInterface
from mega_drive.mdrive import MegaCloudInterface
from configuration_handler import ConfigurationHandler
import threading
import hashlib
import os
import re
import time
import json


class RapidCloudTaskHandler(ConfigurationHandler):
    def __init__(self, path_to_task_object):
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
        file_operation = SplitAndCombineFiles()
        os.popen("cp {} {}".format(self.path, "/tmp/"))
        new_name = self.generate_fragment_hash_string()
        os.popen("mv /tmp/{} /tmp/{}".format(file_name, new_name))
        time.sleep(3)
        divide_scheme = self.get_proper_file_divide_scheme()
        print(divide_scheme)
        file_operation.split("/tmp/{}".format(new_name), divide_scheme)
        self.upload_all_fragments(new_name)
        self.wait_for_transfer_off_all_fragments()
        self.delete_temp_files(new_name)
        self.create_original_file_trace(file_name)

    def create_original_file_trace(self, original_file_name):
        file = open("{}.rp".format(original_file_name), "w")
        file.write(json.dumps(self.file_trace))
        file.close()

    def import_file_from_cloud(self):
        file_name = self.path.split("/")[-1]
        file_operation = SplitAndCombineFiles()
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
        file_operation.merge("/tmp/{}.zip".format(keys_list[-1]).split("-")[0])
        os.popen("cp {} {}".format("/tmp/{}".format(hash_name), "."))
        os.popen("mv {} {}".format(hash_name, "{}.{}".format(file_name.split(".")[0], file_name.split(".")[1])))
        self.delete_temp_files(hash_name)

    def wait_for_transfer_off_all_fragments(self):
        while True:
            self.transfer_finished = True
            for task in self.tasks:
                if not task.finish:
                    self.transfer_finished = False
                    break
            if self.transfer_finished:
                break

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


obj = RapidCloudTaskHandler("20MB.zip.rp")
obj.import_file_from_cloud()
