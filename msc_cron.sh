#!/bin/sh

LOCK_FILE=/tmp/msc_cron.lock
PARSE_LOG=parsed.log
VALIDATE_LOG=validated.log
ARCHIVE_LOG=archived.log

export PATH=$PATH:/usr/local/bin/
cd /home/dev/mastercoin-tools/

# update external prices for wallet view
python msc_prices.py
cp www/currencies.json ../dev-mastercoin-tools/www/

# check lock (not to run multiple times)
[ -f $LOCK_FILE ] && exit 0

# lock
touch $LOCK_FILE

# parse until full success
x=1 # assume failure
echo -n > $PARSE_LOG
while [ "$x" != "0" ];
do
  python msc_parse.py 2>&1 >> $PARSE_LOG
  x=$?
done

python msc_validate.py 2>&1 > $VALIDATE_LOG

# copy all results to web browser directory
cp tx/* www/tx/
cp addr/* www/addr/
cp general/* www/general/
cp bids/* www/bids/
mkdir -p www/mastercoin_verify/addresses/
cp mastercoin_verify/addresses/* www/mastercoin_verify/addresses/
mkdir -p www/mastercoin_verify/transactions/
cp mastercoin_verify/transactions/* www/mastercoin_verify/transactions/

# copy also to dev site
cp tx/* ../dev-mastercoin-tools/www/tx/
cp addr/* ../dev-mastercoin-tools/www/addr/
cp general/* ../dev-mastercoin-tools/www/general/
cp bids/* ../dev-mastercoin-tools/www/bids/
mkdir -p ../dev-mastercoin-tools/www/mastercoin_verify/addresses/
cp mastercoin_verify/addresses/* ../dev-mastercoin-tools/www/mastercoin_verify/addresses/
mkdir -p ../dev-mastercoin-tools/www/mastercoin_verify/transactions/
cp mastercoin_verify/transactions/* ../dev-mastercoin-tools/www/mastercoin_verify/transactions/

# update archive
python msc_archive.py 2>&1 > $ARCHIVE_LOG

# unlock
rm -f $LOCK_FILE
