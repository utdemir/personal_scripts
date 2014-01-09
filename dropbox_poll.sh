#!/bin/sh

while true; do
  sleep 20
  if [[ "$(dropbox status)" == 'Connecting...' ]]; then
    echo "Restarting Dropbox..."
    dropbox stop
    dropbox start
  fi
done
