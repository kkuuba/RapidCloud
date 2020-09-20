from file_split_merge import SplitAndCombineFiles
from utilities import *
import argparse
import threading
import hashlib
import os
import re
import time
import json
import curses


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
        providers_data = self.get_data_from_json()["cloud_providers"]
        number = sum(item["up_link"] for item in providers_data)
        print(number)
        divide_data_scheme = {}
        next_frag_id = 1
        for provider_id in range(len(providers_data)):
            assigned_fragments = int(round((providers_data[provider_id]["up_link"] / number) * 8))
            print(assigned_fragments)
            divide_data_scheme.update(
                {str(provider_id + 1): list(range(next_frag_id, next_frag_id + assigned_fragments))})
            next_frag_id = assigned_fragments + 1

        return divide_data_scheme

    def generate_fragment_hash_string(self):
        return str(hashlib.sha256(self.start.encode("utf-8")).hexdigest())

    def export_file_to_cloud(self):
        with HiddenPrints():
            file_name = self.path.split("/")[-1]
            self.file_encryption.prepare_file_to_export()
            new_name = self.generate_fragment_hash_string()
            os.popen("mv /tmp/{} /tmp/{}".format("{}.zip".format(file_name.split(".")[0]), new_name))
            time.sleep(3)
            divide_scheme = self.get_proper_file_divide_scheme()
            self.file_operation.split("/tmp/{}".format(new_name), str(8))
            self.upload_all_fragments(new_name, divide_scheme)
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
        with HiddenPrints():
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
        with HiddenPrints():
            hash_name = keys_list[-1].split("-")[0]
            self.file_operation.merge("/tmp/{}.zip".format(keys_list[-1]).split("-")[0])
            self.file_encryption = FileEncryption(hash_name, self.encryption_key)
            self.file_encryption.prepare_file_after_import()
            self.delete_temp_files(hash_name)
            self.delete_temp_files("aes")

    def wait_for_transfer_off_all_fragments(self):
        std_scr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        try:
            while True:
                self.transfer_finished = True
                for task in self.tasks:
                    task_id = self.tasks.index(task)
                    if not task.finish:
                        self.transfer_finished = False
                        std_scr.addstr(task_id, 0,
                                       "FRAGMENT_[{}] ----> {} ----------------------- [in progress]\n".format(
                                           task_id + 1, task.provider))
                    else:
                        std_scr.addstr(task_id, 0,
                                       "FRAGMENT_[{}] ----> {} ----------------------- [success]\n".format(
                                           task_id + 1, task.provider))
                if self.transfer_finished:
                    break
                std_scr.refresh()
                time.sleep(0.5)
        finally:
            curses.echo()
            curses.nocbreak()
            curses.endwin()

    def upload_all_fragments(self, new_filename, divide_data_scheme):
        providers_data = self.get_data_from_json()
        UnitDataTransferTask("{}-{}.ros".format(new_filename, "CRC"), 1,
                             providers_data["cloud_providers"][0]["provider"]).export_fragment()
        self.file_trace.update({
            "{}-{}.ros".format(new_filename, "CRC"): providers_data["cloud_providers"][0]
        })
        print(divide_data_scheme)
        for provider in divide_data_scheme:
            for fragment_id in divide_data_scheme[provider]:
                self.file_trace.update({
                    "{}-{}.ros".format(new_filename, fragment_id): providers_data["cloud_providers"][int(provider) - 1]
                })
                self.tasks.append(
                    UnitDataTransferTask("{}-{}.ros".format(new_filename, fragment_id), int(provider),
                                         providers_data["cloud_providers"][int(provider) - 1]["provider"]))
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
    setup_log_file()
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
        parser.add_argument('-t', '--test_network_performance', action='store_true',
                            help="Check up-link speed of all cloud providers")
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
        elif args.test_network_performance:
            check_performance()
        else:
            log_to_console("No proper file provided")
    except KeyboardInterrupt:
        log_to_console("Execution interrupted\n")
        exit()


if __name__ == "__main__":
    main()
