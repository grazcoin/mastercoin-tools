#!/bin/sh

LOCK_FILE=/tmp/msc_cron.lock

[ -f $LOCK_FILE ] && exit 0
touch $LOCK_FILE
export PATH=$PATH:/usr/local/bin/
cd /home/dev/mastercoin-tools/
python msc_parse.py 2>&1 > parsed.log
python msc_validate.py 2>&1 > validated.log
cp tx/* www/tx/
cp addr/* www/addr/
cp general/* www/general/
cp bids/bids-* www/bids/
python msc_archive.py 2>&1 > archived.log
rm -f $LOCK_FILE
