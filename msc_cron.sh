#!/bin/sh

cd ~/mastercoin-tools/
python msc_parse.py && \
    python msc_validate.py && \
    cp tx/* www/tx/ && \
    cp addr/* www/addr/ && \
    cp general/* www/general/ && \
    echo done
