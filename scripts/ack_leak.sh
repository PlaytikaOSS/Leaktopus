#!/usr/bin/env bash

HOST=$1
LEAK_ID=$2

curl --silent -X PATCH "${HOST}/api/leak/${LEAK_ID}" -H "Content-Type: application/json" --data "{\"acknowledged\":true}"
