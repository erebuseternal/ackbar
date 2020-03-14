#!/bin/bash
export LC_ALL=C.UTF-8
export FLASK_APP=/ackbar/datastore/datastore.py
/usr/sbin/sshd -D
flask run --host=0.0.0.0
