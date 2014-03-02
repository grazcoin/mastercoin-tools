#!/usr/bin/python

#######################################################
#                                                     #
#  Copyright Masterchain Grazcoin Grimentz 2013-2014  #
#  https://github.com/grazcoin/mastercoin-tools       #
#  https://masterchain.info                           #
#  masterchain@@bitmessage.ch                         #
#  License AGPLv3                                     #
#                                                     #
#######################################################

f=open('outputs/bootstrap.log','r')
lines=f.readlines()
f.close()

d={}
for l in lines:
    pair=l.strip().split(',')
    address=pair[0]
    amount=int(pair[1])
    if d.has_key(address):
        d[address]+=amount
    else:
        d[address]=amount

items = d.items()
items.sort()
for k in items:
    print k
