#!/bin/bash

export ENVIRONMENT="development"
source /home/jparilla/envs/env/bin/activate
uvicorn main:app --port 8000 --reload
