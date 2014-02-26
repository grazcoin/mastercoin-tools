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
  
    urls_list_dict={'MSC': \
        ['https://masterchain.info/mastercoin_verify/addresses/0', \
        'https://masterchest.info/mastercoin_verify/addresses.aspx', \
        'http://mymastercoins.com/jaddress.aspx?currency_id=1'], \
        'TMSC': \
        ['https://masterchain.info/mastercoin_verify/addresses/1', \
        'https://masterchest.info/mastercoin_verify/addresses_test.aspx', \
        'http://mymastercoins.com/jaddress.aspx?currency_id=2']}

    for coin in urls_list_dict.keys():
        urls=urls_list_dict[coin]

        dicts={}
        for u in urls:
            dicts[url_to_domain(u)]={}

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

        # collect detailed difference in text format
        detailed_difference=coin+' consensus check at '+get_now()+'\n'
        sources=keys[:]
        for addr in difference_dict.keys():
            results=addr+': '
            for source in sources:
                try:
                    value=str(float(dicts[source][addr]))
                except KeyError:
                    value='0.0'
                results+=source+' '+value+'; '
            detailed_difference+=results+'\n'

        atomic_json_dump(difference_dict,'www/general/'+coin+'-difference.json')
        f = open('www/general/'+coin+'-difference.txt', "w")
        f.write(detailed_difference)
        f.close()

    info('comparison done')

if __name__ == "__main__":
    compare()
