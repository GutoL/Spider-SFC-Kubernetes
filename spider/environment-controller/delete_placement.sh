#!/bin/sh

kubectl delete services my-sfc-vnf1-service
kubectl delete services my-sfc-vnf2-service

kubectl delete deployments my-sfc-vnf1
kubectl delete deployments my-sfc-vnf2

