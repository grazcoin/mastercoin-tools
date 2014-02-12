#!/usr/bin/python
import os
import urllib2
from optparse import OptionParser
from msc_utils_validating import *

# get domain name from url
def url_to_domain(u):
    return u.split('//')[1].split('.')[0]

#################################################################
# main function - compares mastercoin_verify of implementations #
#################################################################
def compare():

    # parse command line arguments
    parser = OptionParser("usage: %prog [options]")
    parser.add_option("-d", "--debug", action="store_true",dest='debug_mode', default=False,
                        help="turn debug mode on")

    (options, args) = parser.parse_args()
    msc_globals.init()
    msc_globals.d=options.debug_mode

    info('starting comparison')

    difference_dict={}
   
    urls=['https://masterchain.info/mastercoin_verify/addresses/0', \
          'https://masterchest.info/mastercoin_verify/addresses.aspx', \
          'http://mymastercoins.com/jaddress.aspx']
    # parse sites from url list
    sites=[]
    for u in urls:
        sites.append(url_to_domain(u))
    dicts={sites[0]:{},sites[1]:{},sites[2]:{}}

    keys=dicts.keys()

    for u in urls:
        filename='general/'+url_to_domain(u)+'-addresses.json'
        debug('download json from '+u+' start')
        response = urllib2.urlopen(u)
        f = open(filename, "w")
        f.write(response.read())
        f.close()
        debug('download json from '+u+' done')
        l=load_dict_from_file(filename, all_list=True)
        for d in l:
            dicts[url_to_domain(u)][d['address']]=d['balance']

    for source in keys:
        for addr in dicts[source].keys():
            compare_to=keys[:]
            compare_to.remove(source)
            for other in compare_to:
                try:
                    if float(dicts[source][addr])!=float(dicts[other][addr]):
                        difference_dict[addr]='different'
                except KeyError:
                    if float(dicts[source][addr]) != 0: # 0 is considered as nothing
                        difference_dict[addr]='not on '+other

    atomic_json_dump(difference_dict,'general/difference.json')

    info('comparison done')

if __name__ == "__main__":
    compare()
