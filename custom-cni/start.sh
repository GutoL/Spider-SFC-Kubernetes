#!/bin/sh

# Create and configure the bridge with the cni0 name
sudo brctl addbr cni0
sudo ip link set cni0 up
# You can check the bridge IP using: kubectl describe node k8s-master | grep PodCIDR
# In this case, the IP is 10.244.0.0/24, and you need to replace the last digit: 0->1
sudo ip addr add 10.244.0.1/24 dev cni0

# Apply additional forwarding rules that will allow to freely forward traffic inside the whole pod CIDR range
# This should fix the issues with communication between containers located at the same host.
sudo iptables -t filter -A FORWARD -s 10.244.0.0/16 -j ACCEPT
sudo iptables -t filter -A FORWARD -d 10.244.0.0/16 -j ACCEPT

# Setup NAT using the following command
sudo iptables -t nat -A POSTROUTING -s 10.244.0.0/24 ! -o cni0 -j MASQUERADE

# Create communication between containers on different nodes. You must to add information about all nodes present in the cluster
sudo ip route add 10.244.1.0/24 via 192.168.0.95 dev enp0s3

sudo swapoff -a
sudo systemctl daemon-reload
sudo systemctl restart docker
sudo systemctl restart kubelet

