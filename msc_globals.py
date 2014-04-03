#######################################################
#                                                     #
#  Copyright Masterchain Grazcoin Grimentz 2013-2014  #
#  https://github.com/grazcoin/mastercoin-tools       #
#  https://masterchain.info                           #
#  masterchain@@bitmessage.ch                         #
#  License AGPLv3                                     #
#                                                     #
#######################################################

# globals.py

def init():
    global last_block
    global d # debug mode
    global exodus_scan # exodus address of current chain
    last_block=0
    d=False
    exodus_scan='unknown'
