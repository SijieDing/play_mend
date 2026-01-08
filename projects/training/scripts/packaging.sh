#!/bin/sh

set -e

PROJECT_DIR=$(cd $(dirname "$0"); cd .. ; pwd)
PROJECT_NAME=ap-aa-$(basename "${PROJECT_DIR}")-func

cd "${PROJECT_DIR}"

# prepare dist folder
rm -fr conf
rm -fr dist
mkdir -p conf
mkdir -p dist/scripts
mkdir -p dist/libs

# copy files
cp pyproject.toml dist
cp *.py dist
cp scripts/build.sh dist/scripts
cp Dockerfile dist

# copy libs
# cp ../../libs/aiops_unite_pkg/pyproject.toml dist/libs
cp -r ../../libs/aiops_unite_pkg/aiops_unite dist
cp -r ../../libs/training_pkg/aiops_training dist

# prepare sample conf
cp ../../libs/aiops_unite_pkg/aiops_unite/sample-config.yaml conf/ap-aa-config.yaml

# build image
cd dist/

pip install -e . --no-cache-dir

export IMAGE_NAME="ap-anomaly-detection-training-function"
export IMAGE_PATH_ICR=${GLOBAL_ICR_REPO}/${GLOBAL_ICR_NAMESPACE}/${IMAGE_NAME}
export IMAGE_ICR="${IMAGE_PATH_ICR}:${TRAVIS_TAG:-$TAG_BUILD_NUMBER}${TRAVIS_TAG:+-$BLD_ARCH}"

if [[ "${TRAVIS_TAG}" != "" ]]; then
    docker buildx build --no-cache --platform=linux/${BLD_ARCH} -t ${IMAGE_PATH_ICR}:${TRAVIS_TAG}-${BLD_ARCH} --load --progress=plain .
    docker push --platform=linux/${BLD_ARCH} ${IMAGE_PATH_ICR}:${TRAVIS_TAG}-${BLD_ARCH}
    exit 0
else
    docker buildx build --no-cache --platform=linux/${BLD_ARCH} -t ${IMAGE_ICR} --load --progress=plain .
    docker push --platform linux/${BLD_ARCH} ${IMAGE_ICR}
    docker tag ${IMAGE_ICR} ${IMAGE_PATH_ICR}:${TAG_TIMESTAMP}
    docker push --platform linux/${BLD_ARCH} ${IMAGE_PATH_ICR}:${TAG_TIMESTAMP}
    docker tag ${IMAGE_ICR} ${IMAGE_PATH_ICR}:${TAG_LATEST}
    docker push --platform linux/${BLD_ARCH} ${IMAGE_PATH_ICR}:${TAG_LATEST}
fi