#!/usr/bin/env bash

# Fetch the DB from the web container.
docker cp $(docker ps | grep leaktopus_web | awk '{ print $1 }'):/db/leaktopus.sqlite .
