#!/usr/bin/python
import git
from optparse import OptionParser
from msc_utils import *

d=False # debug_mode

def main():
    parser = OptionParser("usage: %prog [options]")
    parser.add_option("-d", "--debug", action="store_true",dest='debug_mode', default=False,
                        help="turn debug mode on")

    (options, args) = parser.parse_args()
    d=options.debug_mode

    # zip all parsed data and put in downloads
    archive_parsed_data()

if __name__ == "__main__":
    main()
