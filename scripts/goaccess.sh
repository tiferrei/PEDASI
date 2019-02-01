#!/usr/bin/env bash

if [[ "$#" -ne 1 ]]; then
    echo "Requires output file name"
    exit 1
fi

if [[ -f /var/log/nginx/access.log.2.gz ]]; then
    zcat /var/log/nginx/access.log.*.gz | goaccess -q --log-format=COMBINED -o $1 /var/log/nginx/access.log /var/log/nginx/access.log.1 -
elif [[ -f /var/log/nginx/access.log.1 ]]; then
    goaccess -q --log-format=COMBINED -o $1 /var/log/nginx/access.log /var/log/nginx/access.log.1 -
else
    goaccess -q --log-format=COMBINED -o $1 /var/log/nginx/access.log
fi
