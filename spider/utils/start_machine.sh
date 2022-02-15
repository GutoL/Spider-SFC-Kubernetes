#!/bin/sh

sudo swapoff -a

sudo tc qdisc add dev enp0s3 root netem delay 567ms # Tokyo
# sudo tc qdisc del dev enp0s3 root

cd daemon && python3 daemon.py
