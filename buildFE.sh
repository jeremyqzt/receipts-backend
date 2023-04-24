#!/bin/sh
VERSION=$(git log -1 --pretty=%h)

if [ -z "$1" ]
  then
    echo "Native build\n"
    docker build -t jeremyqzt/ribbonfe -f docker/frontend.Dockerfile .
    exit 0
fi

echo "Buildx build\n"
eval "docker buildx build --push --platform=linux/arm64,linux/amd64 -f Docker/frontend.Dockerfile -t jeremyqzt/ribbonfe:$VERSION ."

IMAGE="jeremyqzt/ribbonfe:$VERSION" envsubst < k8s/frontend.yaml | kubectl apply -f -

#docker run \
#    -it \
#    --rm \
#    -v ${PWD}:/app \
#    -v /app/node_modules \
#    -p 3001:3000 \
#    jeremyqzt/ribbonfe