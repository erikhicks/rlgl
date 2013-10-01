#!/bin/bash

printf "RLGL: Starting node server...\n"
cd /home/pi/code/rlgl
forever start -l forever.log --append -o out.log -e err.log app.js

printf "RLGL: Initializing PiFace...\n"
cd /home/pi/code
python changecolor.py init

printf "RLGL: Adding IP address entry to DNSMe...\n"
cd /home/pi/code
python dnsme.py --host rlgl --domain iwantmy.mobi setip `ip -f inet addr show dev wlan0 | sed -n 's/^ *inet *\([.0-9]*\).*/\1/p'`
