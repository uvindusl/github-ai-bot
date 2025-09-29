#!/bin/bash


echo "---- Starting Server ----"

docker compose up & 

smee --url https://smee.io/N2tkdNotkdgliU --target http://localhost:8000/webhooks & 

echo "Webhook and docker is running background"