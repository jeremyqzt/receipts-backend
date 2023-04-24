#!/bin/sh
kubectl apply -f secrets/aws-access-key-id-secret.yaml
kubectl apply -f secrets/aws-secret-access-key-secret.yaml 
kubectl apply -f secrets/db-pass-secret.yaml

kubectl apply -f k8s/backend.yaml
kubectl apply -f k8s/hpa.yaml

kubectl apply -f k8s/frontend.yaml

kubectl apply -f k8s/ingress.yaml
