#!/bin/sh
redis-server --daemonize yes
. venv/bin/activate
/usr/bin/env python3 -m pagermaid
