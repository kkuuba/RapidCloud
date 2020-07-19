from google_drive.gdrive import GoogleDriveInterface
from mega_drive.mdrive import MegaCloudInterface
from configuration_handler import get_data_from_json, modify_account_parameter
import os
import time


class ThroughputTest:
    def __init__(self, account_id):
        self.account_id = account_id
        self.cloud_service = self.create_cloud_provider_instance()
        self.run_service_test()

    def create_cloud_provider_instance(self):
        provider = get_data_from_json(self.account_id)["provider"]
        if provider == "google":
            return GoogleDriveInterface(self.account_id)
        elif provider == "megacloud":
            return MegaCloudInterface(self.account_id)

    def down_link_test(self):
        start_time = time.time()
        self.cloud_service.download_file("20MB.zip")
        return time.time() - start_time

    def up_link_test(self):
        start_time = time.time()
        self.cloud_service.upload_file("20MB.zip")
        return time.time() - start_time

    def run_service_test(self):
        down_link_tput = 20.0 / self.down_link_test()
        up_link_tput = 20.0 / self.up_link_test()
        os.remove("/tmp/20MB.zip")
        modify_account_parameter(self.account_id, "uplink", up_link_tput)
        modify_account_parameter(self.account_id, "downlink", down_link_tput)


while True:
    info = get_data_from_json()
    print(info)
    for account in info["cloud_providers"]:
        ThroughputTest(account["account_id"])
    time.sleep(60)
