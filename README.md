# RapidCloud

Bash tool for safe and efficient file transfers using multiple cloud storage accounts.
Recently Google Drive and MEGA Drive are supported (multiple accounts of same provider can be configured).
All files are encrypted with AES-256 and distributed over configured accounts. After successful upload of file special
marker with .rp extension is created. It can be used to download back exported file. 

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install RapidCloud with .whl file:

```bash
git clone https://github.com/kkuuba/RapidCloud.git
cd RapidCloud
sudo pip3 install builds/rapid_cloud-1.0.0-py2.py3-none-any.whl
```
In case of problems with installation using [pip](https://pip.pypa.io/en/stable/):
```bash
sudo pip3 install --ignore-installed builds/rapid_cloud-1.0.0-py2.py3-none-any.whl
```
## Usage

```bash
user@PC:~$ rapid_cloud -h
usage: rapid_cloud [-h] [-r] [-f] [-p] [-t] [filename]

Manage distributed file transfers to or from multiple cloud storage accounts using AES-256 fragments encryption

positional arguments:
  filename              provide the file to exort or .rp file trace to import data from cloud storage

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
```
