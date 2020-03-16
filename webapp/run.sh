#!/bin/bash
export FLASK_APP=webapp.py
export LC_ALL=C.UTF-8
export FLASK_ENV=development
flask run --host=0.0.0.0 --port=5001