#!/bin/sh
VERSION=$(git log -1 --pretty=%h)

if [ -z "$1" ]
  then
    echo "Native build\n"
    docker build -t jeremyqzt/ribbonbe -f docker/backend.Dockerfile .
    exit 0
fi

echo "Buildx build\n"
eval "docker buildx build --push --platform=linux/arm64,linux/amd64 -f Docker/backend.Dockerfile -t jeremyqzt/ribbonbe:$VERSION ."


IMAGE="jeremyqzt/ribbonbe:$VERSION" envsubst < k8s/backend.yaml | kubectl apply -f -