from google_drive.gdrive import GoogleDriveInterface
from mega_drive.mdrive import MegaCloudInterface
from configuration_handler import ConfigurationHandler
from utilities import UnitDataTransferTask
import os
import time


class ThroughputTest:
    def __init__(self, account_id):
        self.configuration_handler = ConfigurationHandler(account_id)
        self.account_id = account_id
        self.provider = None
        self.cloud_service = self.create_cloud_provider_instance()
        self.run_service_test()

    def create_cloud_provider_instance(self):
        self.provider = self.configuration_handler.get_data_from_json()["provider"]
        if self.provider == "google":
            return GoogleDriveInterface(self.account_id)
        elif self.provider == "megacloud":
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
        data = self.cloud_service.get_info_about_file("20MB.zip")
        if data:
            down_link_tput = 20.0 / self.down_link_test()
            up_link_tput = 20.0 / self.up_link_test()
        else:
            os.popen("cp test_files/20MB.zip /tmp")
            UnitDataTransferTask("20MB.zip", self.account_id, self.provider).export_fragment()
            down_link_tput = 20.0 / self.down_link_test()
            up_link_tput = 20.0 / self.up_link_test()
        os.remove("/tmp/20MB.zip")
        self.configuration_handler.modify_account_parameter("uplink", up_link_tput)
        self.configuration_handler.modify_account_parameter("downlink", down_link_tput)


while True:
    configuration_handler = ConfigurationHandler()
    info = configuration_handler.get_data_from_json()
    print(info)
    for account in info["cloud_providers"]:
        ThroughputTest(account["account_id"])
    time.sleep(60)
