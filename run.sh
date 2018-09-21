#!/bin/bash
PORT=${1:-80}
sudo docker run -it --name safecast-api -v $HOME:$HOME -p $PORT:5000 safecast-api
