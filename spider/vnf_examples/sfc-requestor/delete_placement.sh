#!/bin/sh

kubectl delete deployments my-sfc-compress-image
kubectl delete deployments my-sfc-firewall
kubectl delete deployments my-sfc-face-detection

kubectl delete services my-sfc-compress-image-service
kubectl delete services my-sfc-firewall-service
kubectl delete services my-sfc-face-detection-service
