from file_split_merge import SplitAndCombineFiles
from configuration_handler import ConfigurationHandler
from utilities import *
import argparse
import threading
import hashlib
import os
import re
import time
import json


class RapidCloudTaskHandler(ConfigurationHandler):
    def __init__(self, path_to_task_object):
        super().__init__()
        self.file_operation = SplitAndCombineFiles()
        self.encryption_key = self.get_rapid_cloud_password()
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
        back_up_trace_file = open(
            "/home/{}/.config/rapid_cloud_data/exported_files/{}.rp".format(user_name,
                                                                            original_file_name.split(".")[0]), "w")
        back_up_trace_file.write(json.dumps(self.file_trace))
        back_up_trace_file.close()

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


def main():
    try:
        parser = argparse.ArgumentParser(
            description='Export or import file to or from multiple cloud storage providers')
        parser.add_argument('filename', nargs='?', default="none",
                            help="Provide the File that needs to be exported or imported")
        parser.add_argument('-r', '--reset_configuration', action='store_true',
                            help="Wipe out actual accounts configuration")
        parser.add_argument('-S', '--show_cloud_files', action='store_true',
                            help="Show all files exported to cloud")
        parser.add_argument('-p', '--show_cloud_parameters', action='store_true',
                            help="Show all cloud providers parameters")
        prepare_all_accounts()
        args = parser.parse_args()
        is_valid_file = os.path.exists(args.filename)
        if args.filename.split(".")[-1] == "rp" and is_valid_file:
            transfer_obj = RapidCloudTaskHandler(args.filename)
            transfer_obj.import_file_from_cloud()
        elif args.filename and is_valid_file:
            transfer_obj = RapidCloudTaskHandler(args.filename)
            transfer_obj.export_file_to_cloud()
        elif args.reset_configuration:
            reset_configuration()
        elif args.show_cloud_files:
            show_cloud_files()
        elif args.show_cloud_parameters:
            show_cloud_parameters()
        else:
            log("No proper file provided")
    except KeyboardInterrupt:
        log("Execution interrupted\n")
        exit()


if __name__ == "__main__":
    main()
