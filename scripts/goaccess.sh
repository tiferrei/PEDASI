#!/usr/bin/env bash

if [[ "$#" -ne 1 ]]; then
    echo "Requires output file name"
    exit 1
fi

if [[ -f /var/log/nginx/access.log.1.gz ]]; then
    zcat /var/log/nginx/access.log.*.gz | goaccess --log-format=COMBINED -o $1 /var/log/nginx/access.log -
else
    goaccess --log-format=COMBINED -o $1 /var/log/nginx/access.log
fi
