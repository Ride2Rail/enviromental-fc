#!/bin/bash
app="environmental-fc"
docker build -t ${app} .
docker run -d -p 5008:5008 \
  --name=${app} \
  -v $PWD:/app ${app}
