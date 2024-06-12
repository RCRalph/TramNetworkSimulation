#!/bin/bash

source /home/apps/Personal/TramNetworkSimulation/.venv/bin/activate
exec gunicorn --workers 2 --bind localhost:3001 app:app
