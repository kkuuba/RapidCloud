import dropbox

dbx = dropbox.Dropbox("yHDbfnbz9-AAAAAAAAAAIP93zSRmdzxacgIRH8eYh2zq2xsSakkodtabShcnrHhM")
dbx.users_get_current_account()


class TransferData:
    def __init__(self, access_token):
        self.access_token = access_token

    def upload_file(self, file_from, file_to):
        """upload a file to Dropbox using API v2
        """
        dbx = dropbox.Dropbox(self.access_token)

        with open(file_from, 'rb') as f:
            dbx.files_upload(f.read(), file_to)


transferData = TransferData("yHDbfnbz9-AAAAAAAAAAIP93zSRmdzxacgIRH8eYh2zq2xsSakkodtabShcnrHhM")

file_from = 'test.txt'
file_to = '/test_dropbox/test1.txt'  # The full path to upload the file to, including the file name

transferData.upload_file(file_from, file_to)

