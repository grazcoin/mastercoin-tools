#!/bin/sh

uwsgi -s 127.0.0.1:1088 -M --vhost --plugin python
