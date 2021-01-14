# RapidCloud

Bash tool for safe and efficient file transfers using multiple cloud storage accounts.
Recently Google Drive and MEGA Drive are supported (multiple accounts of same provider can be configured).
All files are encrypted with AES-256 and distributed over configured accounts. After successful upload of file special
marker with .rp extension is created. It can be used to download back exported file. 

## Installation

Use the dpkg manager to install application with ".deb" file:

```bash
git clone https://github.com/kkuuba/RapidCloud.git
cd RapidCloud
sudo chmod +x install.sh
./install.sh
```
First execution and accounts configuration:
```bash
rapid_cloud -p
```
## Usage

```bash
user@PC:~$ rapid_cloud -h
usage: rapid_cloud [-h] [-r] [-f] [-p] [-t] [-e] [-i] [filename]

Manage distributed file transfers to or from multiple cloud storage accounts using AES-256 fragments encryption

positional arguments:
  filename              provide the file to export or .rp file trace to import data from cloud storage

optional arguments:
  -h, --help            show this help message and exit
  -r, --reset_configuration
                        wipe out all actual accounts configuration
  -f, --show_cloud_files
                        show all files exported from this machine to cloud storage
  -p, --show_cloud_parameters
                        show all cloud storage accounts parameters
  -t, --test_network_performance
                        check up-link speed of all cloud storage accounts
  -e, --export_user_configuration
                        export user configuration to .rpconf file
  -i, --import_user_configuration
                        import user configuration from .rpconf file
```
