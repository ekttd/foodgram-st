#!/bin/sh

if [ -d "/app/build" ]; then
  cp -r /app/build/. /static/
else
  exit 1
fi

tail -f /dev/null
