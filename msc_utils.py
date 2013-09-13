#!/usr/bin/python
import subprocess
import json
import simplejson

exodus_address='1EXoDusjGwvnjZUyKkxZ4UHEf77z6A5S4P'
first_exodus_bootstrap_block=249498
last_exodus_bootstrap_block=255365
exodus_bootstrap_deadline=1377993600
currency_type_dict={'00000001':'Mastercoin','00000002':'Test Mastercoin'}
transaction_type_dict={'00000000':'Simple send'}

def run_command(command, input_str=None):
    if input_str!=None:
        p = subprocess.Popen(command, shell=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)
        return p.communicate(input_str)
    else:
        p = subprocess.Popen(command, shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)
        return p.communicate()

def get_block_timestamp(height):
    raw_block, err = run_command("sx fetch-block-header "+str(height))
    if err != None:
        return err
    else:
        block_details, err = run_command("sx showblkhead", raw_block)
        if err != None:
            return err
        else:
            for line in block_details.split('\n'):
                if line.startswith('timestamp:'):
                    timestamp=int(line.split('timestamp: ')[1])
                    return timestamp

def get_raw_tx(tx_hash):
    out, err = run_command("sx fetch-transaction "+tx_hash)
    if err != None:
        return err
    else:
        return out

def get_json_tx(raw_tx, tx_hash='unknown hash'):
    json_tx, err = run_command("sx showtx -j", raw_tx)
    if err != None:
        error('get_json_tx: ' + err)
    else:
        try:
            parsed_json_tx=simplejson.JSONDecoder().decode(json_tx)
        except simplejson.JSONDecodeError:
            error('error parsing json_tx: '+str(json_tx)+' '+str(tx_hash))
    return parsed_json_tx

def get_tx(tx_hash):
    raw_tx=get_raw_tx(tx_hash)
    return get_json_tx(raw_tx, tx_hash)

def get_json_history(addr):
    out, err = run_command("sx history -j "+addr)
    if err != None:
        return err
    else:
        return out

def get_history(addr):
    json_history=get_json_history(addr)
    try:
        parsed_json_history=simplejson.JSONDecoder().decode(json_history)
    except simplejson.JSONDecodeError:
        error('error parsing json_history')
    return parsed_json_history

# used as a key function for sorting history
def output_height(item):
    return item['output_height']

# used as a key function for sorting outputs of msc tx
def get_dataSequenceNum(item):
    try:
        data_script=item['script'].split()[3].zfill(42)
        dataSequenceNum=data_script[2:4]
        return dataSequenceNum
    except KeyError, IndexError:
        return None

def get_currency_type(currencyId):
    if currency_type_dict.has_key(currencyId):
        return currency_type_dict[currencyId]
    else:
        return 'Unknown currency id '+str(currencyId)

def get_transaction_type(transactionType):
    if transaction_type_dict.has_key(transactionType):
        return transaction_type_dict[transactionType]
    else:
        return 'Unknown transaction type '+str(transactionType)


def error(msg):
    print '[E]: '+str(msg)
    exit(1)

def info(msg):
    print '[I]: '+str(msg)

# output_format is 'story' for long description of 'csv' for a short one
def output_per_tx(output_format, block, tx_hash, value, dacoins):
    if output_format == 'story':
        print 'block ' + str(block) + ' tx hash ' + str(tx_hash) + \
                ' value ' +str(value) + ' -> ' + str(dacoins) + ' dacoins'
    else:
        pass
# output_format is 'story' for long description of 'csv' for a short one
def output_per_address(output_format, address, dacoins):
    if output_format == 'story':
        print str(address) + ' got ' + dacoins + ' dacoin'
    else:
        print str(address) + ',' + dacoins
