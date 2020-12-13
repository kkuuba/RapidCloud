#!/bin/sh

sudo apt install git-all
sudo apt install python3-pip
git clone https://github.com/kkuuba/RapidCloud.git
sudo pip3 install RapidCloud/builds/rapid_cloud-1.0.0-py2.py3-none-any.whl
rapid_cloud -p
