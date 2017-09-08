#!/bin/bash
#
# Usage:
# # sudo su postgres
# $ sh import-engine-dump.sh ./engine-db.dump
# 
# engine# <select cmd here> 
#
pg_restore -c -e -f /tmp/engine -F t -U postgres $1
psql -U postgres <<< "DROP DATABASE engine"
psql -U postgres <<< "CREATE DATABASE engine"
psql -U postgres engine < /tmp/engine
psql -U postgres engine
