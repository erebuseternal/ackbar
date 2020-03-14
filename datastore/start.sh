#!/bin/bash
export LC_ALL=C.UTF-8
export FLASK_APP=/ackbar/datastore/datastore.py
flask run --host=0.0.0.0
