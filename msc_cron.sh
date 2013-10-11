#!/bin/sh

cd /home/dev/mastercoin-tools/
python msc_parse.py
python msc_validate.py
cp --no-clobber tx/* www/tx/
cp --no-clobber addr/* www/addr/
cp --no-clobber general/* www/general/
python msc_archive.py
