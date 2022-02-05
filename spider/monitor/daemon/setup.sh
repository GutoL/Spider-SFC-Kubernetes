#!/bin/sh

pip3 install Flask
pip3 install flask-classful -U
pip3 install psutil

sudo apt update
sudo apt install vnstat ethtool -y 

