#!/bin/sh

# sudo kubeadm reset

# sudo kubeadm init --pod-network-cidr=10.244.0.0/16

# kubectl config set-cluster kubernetes --server=https://new-master-node-IP:6443>

# Obs.: you need to run this file after reset the cluster and join the nodes again

mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config

kubectl apply -f https://raw.githubusercontent.com/coreos/flannel/master/Documentation/kube-flannel.yml

kubectl create -f pod_authorization.yaml

unset KUBECONFIG
mv $HOME/.kube $HOME/.kube.bak
mkdir $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config


sudo systemctl daemon-reload
sudo systemctl restart docker
sudo systemctl restart kubelet

sleep(5) # sleep 5 seconds...

kubectl taint nodes  sansa-stark node-role.kubernetes.io/master-
kubectl label nodes sansa-stark nodetype=sansa-stark
kubectl label nodes ned-stark nodetype=ned-stark
kubectl label nodes daenerys-targaryen nodetype=daenerys-targaryen 
kubectl label nodes aerys-targaryen nodetype=aerys-targaryen
kubectl label nodes tyrion-lannister nodetype=tyrion-lannister
kubectl label nodes cersei-lannister nodetype=cersei-lannister



