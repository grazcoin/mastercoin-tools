#!/bin/sh

LOCK_FILE=/tmp/msc_compare_cron.lock
COMPARE_LOG=compare.log

export PATH=$PATH:/usr/local/bin/
cd /home/dev/mastercoin-tools/

# check lock (not to run multiple times)
[ -f $LOCK_FILE ] && exit 0

# lock
touch $LOCK_FILE

python msc_compare.py 2>&1 > $COMPARE_LOG

# copy results to web browser directory
cp -f general/difference.json www/general/

# unlock
rm -f $LOCK_FILE
