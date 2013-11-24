#!/usr/bin/python
import operator
from optparse import OptionParser
from msc_utils_parsing import *

def parse():
    msc_globals.init()

    parser = OptionParser("usage: %prog [options]")
    parser.add_option("-d", "--debug", action="store_true",dest='debug_mode', default=False,
                        help="turn debug mode on")
    parser.add_option("-t", "--transaction",dest='single_tx',default=None,
                        help="hash of a specific tx to parse")
    parser.add_option("-s", "--start-block",dest='starting_block_height',default=None,
                        help="start the parsing at a specific block height (default is last)")
    parser.add_option("-a", "--archive-parsed-data", action="store_true",dest='archive', default=False,
                        help="archive the parsed data of tx addr and general for others to download")

    (options, args) = parser.parse_args()
    d=options.debug_mode
    single_tx=options.single_tx
    requested_block_height=options.starting_block_height
    if requested_block_height == None:
        # which block to start with?
        revision_block_height=0 # init with 0
        notes_block_height=0    # init with 0
        # first check last block on revision.json
        filename='www/revision.json'
        try:
            prev_revision_dict=load_dict_from_file(filename, all_list=True, skip_error=True)
            revision_block_height=prev_revision_dict['last_block']
        except KeyError:
            info(filename+' does not have last_block entry')

        # then check LAST_BLOCK_NUMBER_FILE
        try:
            f=open(LAST_BLOCK_NUMBER_FILE, 'r')
            notes=f.readline()
            f.close()
            # FIXME: catch ValueError ?
            if notes != '':
                notes_block_height=int(notes)
        except IOError:
            info(LAST_BLOCK_NUMBER_FILE+' does not exist or has no integer.')

        # take the latest block of all
        starting_block_height=max(revision_block_height,notes_block_height)
        msc_globals.last_block=starting_block_height

    else:
        starting_block_height=requested_block_height

    archive=options.archive

    info('starting parsing at block '+str(starting_block_height))

    if single_tx == None:
        # get all tx of exodus address
        history=get_history(exodus_address)
        history.sort(key=output_height)
    else:
        # build fake history of length 1 (debug purposes)
        json_tx=get_json_tx(get_raw_tx(single_tx))
        marker_number=-1
        marker_value=-1
        i=0
        for o in json_tx['outputs']:
            if o['address']==exodus_address:
                marker_number=i
                marker_value=o['value']
                # FIXME: handle multiple outputs to 1EXoDus
                break
            else:
                i+=1
        if marker_number == -1:
            error('tx does not belong to exodus')

        t1={"output": single_tx+':'+str(marker_number),
        "output_height":"0",
        "value":  str(marker_value)}
        history=[]
        history.append(t1)

    # go over transaction from all history of 1EXoDus address
    last_block=0
    for tx_dict in history:
        value=tx_dict['value']
        if starting_block_height != None:
            current_block=tx_dict['output_height']
            if current_block != 'Pending':
                if int(current_block)<int(starting_block_height):
                    debug('skip block '+str(current_block)+' since starting at '+str(starting_block_height))
                    continue
            else:
                # Pending block will be checked whenever they are not Pending anymore.
                continue
        try:
            tx_hash=tx_dict['output'].split(':')[0]
            tx_output_index=tx_dict['output'].split(':')[1]
        except KeyError, IndexError:
            error("Cannot parse tx_dict:" + str(tx_dict))
        raw_tx=get_raw_tx(tx_hash)
        json_tx=get_json_tx(raw_tx, tx_hash)
        if json_tx == None:
            error('failed getting json_tx (None) for '+tx_hash)
        (block,index)=get_tx_index(tx_hash)
        if block == None or block == "failed:" or index == None:
            error('failed getting block None or index None for '+tx_hash)
        if last_block < int(block):
            last_block = int(block)
        # examine the outputs
        outputs_list=json_tx['outputs']
        # if we're here, then 1EXoDus is within the outputs. Remove it, but ...
        outputs_list_no_exodus=[]
        outputs_to_exodus=[]
        different_outputs_values={}
        for o in outputs_list:
            if o['address']!=exodus_address:
                outputs_list_no_exodus.append(o)
            else:
                outputs_to_exodus.append(o)
            output_value=o['value']
            if different_outputs_values.has_key(output_value):
                different_outputs_values[output_value]+=1
            else:
                different_outputs_values[output_value]=1
        # take care if multiple 1EXoDus exist (for the case that someone sends msc
        # to 1EXoDus, or have 1EXoDus as change address)
        if len(outputs_to_exodus) != 1:
            # add all but the marker outputs
            info("not implemented tx with multiple 1EXoDus outputs: "+tx_hash)
            continue
        num_of_outputs=len(outputs_list)
        (block_timestamp, err)=get_block_timestamp(int(block))
        if block_timestamp == None:
            error('failed getting block timestamp of '+str(block)+': '+err)

        # check if basic or multisig
        is_basic=True
        for o in outputs_list:
            if is_script_multisig(o['script']):
                debug('multisig tx found: '+tx_hash)
                is_basic=False
                break

        if is_basic: # basic option - not multisig
            if num_of_outputs > 2: # for reference, data, marker
                after_bootstrap=int(block)>int(last_exodus_bootstrap_block)
                parsed=parse_simple_basic(raw_tx, tx_hash, after_bootstrap)
                parsed['method']='basic'
                parsed['block']=str(block)
                parsed['index']=str(index)
                if not parsed.has_key('invalid'):
                    parsed['invalid']=False
                parsed['tx_time']=str(block_timestamp)+'000'
                debug(str(parsed))
                filename='tx/'+parsed['tx_hash']+'.json'
                orig_json=None
                try:
                    # does this tx exist? (from bootstrap)
                    f=open(filename, 'r')
                    debug(filename)
                    try:
                        orig_json=json.load(f)[0]
                    except (KeyError, ValueError):
                        try:
                            orig_json=json.load(f)
                        except ValueError:
                            error('failed loading json from '+filename)
                    f.close()
                    # verify bootstrap block
                    if orig_json.has_key('block'):
                        orig_block=orig_json['block']
                        debug('found this tx already on (previous) block '+orig_block)
                        if int(orig_block)>last_exodus_bootstrap_block:
                            debug('but it is post exodus - ignoring')
                            orig_json=None
                    else:
                        info('previous tx without block on '+filename)
                except IOError:
                     pass
                if orig_json != None: # it was an exodus tx
                    if len(orig_json)==1:
                        new_json=[orig_json[0],parsed]
                        atomic_json_dump(new_json, filename, add_brackets=False)
                        info('basic tx was also exodus on '+tx_hash)
                    else:
                        info('basic tx is already present on exodus on '+tx_hash)
                else:
                    atomic_json_dump(parsed, filename)
            else: # num_of_outputs <= 2 and not multisig
                # could still be a bitcoin payment for a sell/buy offer
                if int(block)>int(last_exodus_bootstrap_block):
                    parsed=parse_bitcoin_payment(raw_tx, tx_hash)
                    parsed['method']='bitcoin payment'
                    parsed['block']=str(block)
                    parsed['index']=str(index)
                    parsed['tx_time']=str(block_timestamp)+'000'
                    debug(str(parsed))
                    filename='tx/'+parsed['tx_hash']+'.json'
                    atomic_json_dump(parsed, filename)
                else:
                    debug('skip bootstrap basic tx with less than 3 outputs '+tx_hash)
        else: # multisig
            if num_of_outputs == 2: # simple version of multisig
                parsed=parse_multisig_simple(raw_tx, tx_hash)
                if len(parsed) == 0:
                    # disabled
                    continue
                parsed['method']='multisig simple'
                parsed['block']=str(block)
                parsed['index']=str(index)
                if not parsed.has_key('invalid'):
                    parsed['invalid']=False
                parsed['tx_time']=str(block_timestamp)+'000'
                debug(str(parsed))
                filename='tx/'+parsed['tx_hash']+'.json'
                atomic_json_dump(parsed, filename)
            else:
                if num_of_outputs > 2: # multisig
                    parsed=parse_multisig(raw_tx, tx_hash)
                    if len(parsed) == 0:
                        # disabled
                        continue
                    parsed['method']='multisig'
                    parsed['block']=str(block)
                    parsed['index']=str(index)
                    if not parsed.has_key('invalid'):
                        parsed['invalid']=False
                    parsed['tx_time']=str(block_timestamp)+'000'
                    debug(str(parsed))
                    filename='tx/'+parsed['tx_hash']+'.json'
                    atomic_json_dump(parsed, filename)
                else: # invalid
                    info('multisig with a single output tx found: '+tx_hash)

        # update global block height
        if single_tx == None and block != None:
            msc_globals.last_block=block

    rev=get_revision_dict(last_block)
    atomic_json_dump(rev, 'www/revision.json', add_brackets=False)

    if archive:
        archive_parsed_data()

if __name__ == "__main__":
    parse()
