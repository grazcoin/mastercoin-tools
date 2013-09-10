#!/usr/bin/python
import subprocess
import json
import simplejson

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

def get_json_tx(raw_tx):
    out, err = run_command("sx showtx -j", raw_tx)
    if err != None:
        return err
    else:
        return out

def get_tx(tx_hash):
    raw_tx=get_raw_tx(tx_hash)
    json_tx=get_json_tx(raw_tx)
    try:
        parsed_json_tx=simplejson.JSONDecoder().decode(json_tx)
    except JSONDecodeError:
        error('error parsing json_tx: '+str(json_tx))
    return parsed_json_tx

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
    except JSONDecodeError:
        error('error parsing json_history')
    return parsed_json_history

# used as a key function for sorting
def output_height(item):
    return item['output_height']

def error(msg):
    print '[E]: '+str(msg)
    exit(1)

# output_format is 'story' for long description of 'csv' for a short one
def output_per_tx(output_format, block, tx_hash, value, dacoins):
    if output_format == 'story':
        print 'block ' + str(block) + ' tx hash ' + str(tx_hash) + \
                ' value ' +str(value) + ' -> ' + str(dacoins) + ' dacoins'
    else:
        pass
# output_format is 'story' for long description of 'csv' for a short one
def output_per_address(output_format, address, output_value, dacoins, outputs_sum):
    formatted_dacoins=str('{:.0f}'.format((output_value+0.0)*int(dacoins)/outputs_sum))
    if output_format == 'story':
        print str(address) + ' sent ' + str(output_value) + \
            ' satoshi and got ' + formatted_dacoins + ' dacoin'
    else:
        print str(address) + ',' + formatted_dacoins
