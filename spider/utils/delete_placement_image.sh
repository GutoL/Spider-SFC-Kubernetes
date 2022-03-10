#!/bin/sh

kubectl delete deployments my-sfc-destination-spider-proxy-0
kubectl delete deployments my-sfc-source
kubectl delete deployments my-sfc-destination
kubectl delete deployments my-sfc-compress-image
kubectl delete deployments my-sfc-firewall
kubectl delete deployments my-sfc-face-detection

kubectl delete services my-sfc-destination-spider-proxy-0-service
kubectl delete services my-sfc-source-service
kubectl delete services my-sfc-destination-service
kubectl delete services my-sfc-compress-image-service
kubectl delete services my-sfc-firewall-service
kubectl delete services my-sfc-face-detection-service

