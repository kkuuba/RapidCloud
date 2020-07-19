from file_split_merge import SplitAndCombineFiles
from configuration_handler import get_data_from_json
from google_drive.gdrive import GoogleDriveInterface
from mega_drive.mdrive import MegaCloudInterface
import hashlib
import os, re
import time


def get_proper_file_divide_scheme():
    """
    Here will be code to obtain file spliting

    :return:
    """
    providers_count = len(get_data_from_json()["cloud_providers"])
    if providers_count == 0:
        GoogleDriveInterface()
        MegaCloudInterface()
    return str(len(get_data_from_json()["cloud_providers"]))


def generate_fragment_hash_string():
    return str(hashlib.sha256(str(time.time()).encode("utf-8")).hexdigest())


def export_file_to_cloud(file_path):
    file_name = file_path.split("/")[-1]
    file_operation = SplitAndCombineFiles()
    os.popen("cp {} {}".format(file_path, "/tmp/"))
    new_name = generate_fragment_hash_string()
    os.popen("mv /tmp/{} /tmp/{}".format(file_name, new_name))
    time.sleep(3)
    divide_scheme = get_proper_file_divide_scheme()
    print(divide_scheme)
    file_operation.split("/tmp/{}".format(new_name), divide_scheme)
    upload_all_fragments(new_name, divide_scheme)
    delete_temp_files(new_name)


def upload_fragment(file_name, provider_id):
    provider = get_data_from_json(provider_id)["provider"]
    if provider == "google":
        GoogleDriveInterface(provider_id).upload_file(file_name)
    elif provider == "megacloud":
        MegaCloudInterface(provider_id).upload_file(file_name)


def upload_all_fragments(file_name, divide_scheme):
    for fragment_id in range(1, int(divide_scheme) + 1):
        upload_fragment("{}-{}.ros".format(file_name, fragment_id), fragment_id)
        print(fragment_id)


def delete_temp_files(filename):
    pattern = r"{}*.".format(filename)
    for root, dirs, files in os.walk("/tmp"):
        for file in filter(lambda x: re.match(pattern, x), files):
            os.remove(os.path.join(root, file))

# export_file_to_cloud("/home/kuba/Workspace/repos/RapidCloud/test_files/100MB.zip")
