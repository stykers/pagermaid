#!/usr/bin/env bash
redis-server --daemonize yes
source venv/bin/activate
/usr/bin/env python3 -m jarvis
