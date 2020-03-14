#!/bin/bash
/usr/sbin/sshd -D
flask run --host=0.0.0.0
