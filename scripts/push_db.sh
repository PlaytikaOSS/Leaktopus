#!/usr/bin/env bash

# Push local DB to the web container.
docker cp ./leaktopus.sqlite $(docker ps | grep leaktopus_web | awk '{ print $1 }'):/db/leaktopus.sqlite
docker exec -it --user root $(docker ps | grep leaktopus_web | awk '{ print $1 }') /bin/sh -c "chown python:python /db/leaktopus.sqlite && ls -la /db"