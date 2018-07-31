#!/bin/bash
PORT=${1:-4088}
${DOCKER_CMD} run -it --name $USER.gpu-dashboard -v $HOME:$HOME -p $PORT:5000 $USER/gpu-dashboard
