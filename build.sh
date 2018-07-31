#!/usr/bin/env bash
_USER=${1:-`whoami`}
DOCKER_CMD=${DOCKER_CMD:-'sudo docker'}

${DOCKER_CMD} build --build-arg user=$_USER user-verifier-api .
