from google_drive.gdrive import GoogleDriveInterface
from mega_drive.mdrive import MegaCloudInterface
from zipfile import ZipFile
import pyAesCrypt
from os.path import basename


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


class FileEncryption:
    def __init__(self, file_name, password):
        self.file_name = file_name
        self.password = password
        self.ciphering = pyAesCrypt
        self.buffer_size = 64 * 1024

    def encryption(self):
        self.ciphering.encryptFile(self.file_name, "/tmp/{}".format(self.file_name + ".aes"), self.password,
                                   self.buffer_size)

    def decryption(self):
        self.ciphering.decryptFile("/tmp/{}".format(self.file_name), self.file_name.replace(".aes", ""), self.password,
                                   self.buffer_size)

    def zip_file(self):
        with ZipFile("/tmp/{}.zip".format(self.file_name.split(".")[0]), 'w') as zip_archive:
            path = "/tmp/{}.aes".format(self.file_name)
            zip_archive.write(path, basename(path))
        print('File zipped successfully!')

    def unzip_file(self):
        with ZipFile("/tmp/{}".format(self.file_name), 'r') as zip_archive:
            self.file_name = zip_archive.namelist()[0]
            zip_archive.extractall("/tmp/")
        print('Extracting all the files now...')

    def prepare_file_to_export(self):
        self.encryption()
        self.zip_file()

    def prepare_file_after_import(self):
        self.unzip_file()
        self.decryption()
