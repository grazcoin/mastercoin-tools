#!/bin/sh

LOCK_FILE=/tmp/mint2b_cron.lock
MINT_PARSE_LOG=mint-parsed.log
PRICES_LOG=prices.log
PARSE_LOG=parsed.log
VALIDATE_LOG=validated.log
ARCHIVE_LOG=archived.log
TOOLS_DIR=/home/dev/masterchain-mint2b/mastercoin-tools/

export PATH=$PATH:/usr/local/bin/
cd $TOOLS_DIR

# check lock (not to run multiple times)
[ -f $LOCK_FILE ] && exit 0

# lock
touch $LOCK_FILE

# parse mint until full success
x=1 # assume failure
echo -n > $MINT_PARSE_LOG
while [ "$x" != "0" ];
do
  python msc_mint_parse.py -r $TOOLS_DIR 2>&1 >> $PARSE_LOG
  x=$?
done

python msc_prices.py 2>&1 >> $PRICES_LOG

# parse until full success
x=1 # assume failure
echo -n > $PARSE_LOG
while [ "$x" != "0" ];
do
  python msc_parse.py -r $TOOLS_DIR 2>&1 >> $PARSE_LOG
  x=$?
done

python msc_validate.py -d 2>&1 > $VALIDATE_LOG

# copy all results to web browser directory
#cp tx/* www/tx/
#cp addr/* www/addr/
#cp general/* www/general/
#cp offers/* www/offers/
mkdir -p www/mastercoin_verify/addresses/
mkdir -p www/mastercoin_verify/transactions/

# update archive
#mkdir -p www/downloads/
#python msc_archive.py 2>&1 > $ARCHIVE_LOG

# unlock
rm -f $LOCK_FILE
