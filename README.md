mastercoin-tools
================

## What is it? ##
* Package of mastercoin related tools.
* The intention is to help finalizing the mastercoin spec, and enable easy further coding.


## Based on what? ##
* The code uses the package sx, which is libbitcoin based.
* bugfixes for sx as well as new features like BIP11 and get-pubkey which are needed
in mastercoin-tools got merged:
https://github.com/spesmilo/sx/commits?author=grazcoin


## Aim of this package ##
* Live update - direct "realtime" interaction with the bitcoin network (using
  sx).
* Multi platform - python runs on any arch.
* No additional database is needed (obelisk has its own and can be used
  remotely, and the parser/validator use filesystem and a python dict).
* Alternative code base - use libbitcoin instead of "satoshi client".
* Simple cool and mobile friendly web UI.
* Send transaction directly using a hybrid web wallet (not "Advisor").
* Support for offline wallets.
* Generate parsed data snapshots for download.
* Low CPU requirement on server side (server serves static html files and json
  which are rendered on the client side).
* API (json).


## Let's see something ##

### Already implemented ###

* Web UI with focus on usability. Mobile phones and Tablets friendly:
  https://masterchain.info
  transaction and addresses can be explored by following links
* Built in API:
 * Transactions: https://masterchain.info/tx/$TX_ID.json
 * Addresses: https://masterchain.info/addr/$ADDR.json
 * Latest transactions: https://masterchain.info/general/$CURRENCY_$PAGE_NUMBER.json
* Mastercoin verification
 * Mastercoin addresses balances: https://masterchain.info/mastercoin_verify/addresses/0
 * TMSC addresses balances: https://masterchain.info/mastercoin_verify/addresses/1
 * Transactions per address: https://masterchain.info/mastercoin_verify/transactions/
* Consensus checker:
 * https://masterchain.info/general/MSC-difference.txt
 * https://masterchain.info/general/MSC-difference.json
* Distibuted exchange (currently only TMSC is supported, but soon MSC is enabled)
* Basic hybrid web wallet
 * Wallet: https://masterchain.info/wallet.html
 * Send/Sell/Accept forms for BTC or T/MSC:
   https://masterchain.info/sendform.html?addr=182osbPxCo88oaSX4ReJwUr9uAcchmJVaL&currency=MSC
 * Orderbook: https://masterchain.info/index.html?currency=TMSC&filter=sell
 * Last deals: https://masterchain.info/index.html?currency=TMSC&filter=accept
 * Offline transaction: https://masterchain.info/offlinesign.html


### Example UI pages ###

TMSC on example address showing distributed exchange activity:
https://masterchain.info/Address.html?addr=1BKpa19m5Xy9SvSzC5djPWtCfbuynSDwmb&currency=TMSC

MSC on mastercoin-tools tips jar address:
https://masterchain.info/Address.html?addr=182osbPxCo88oaSX4ReJwUr9uAcchmJVaL&currency=MSC


### Known forks ###

https://github.com/mastercoin-MSC/omniwallet
There you could also find better detailed documentation for API (including
wallet), json format, etc.


### Parsing usage examples ###
```
$ python msc_parse.py -h
Usage: msc_parse.py [options]

Options:
  -h, --help            show this help message and exit
  -d, --debug           turn debug mode on
  -t SINGLE_TX, --transaction=SINGLE_TX
                        hash of a specific tx to parse
  -s STARTING_BLOCK_HEIGHT, --start-block=STARTING_BLOCK_HEIGHT
                        start the parsing at a specific block height (default
                        is last)
  -a, --archive-parsed-data
                        archive the parsed data of tx addr and general for
                        others to download
```

```
$ python msc_parse.py -t aa64fd6088532156a37670e6cbd175c74bb101f1406517613a1a0ae6bc02fb02
[I] main: {'currency_type_str': 'Mastercoin', 'transaction_type_str': 'Simple send', 'currencyId': '00000001', 'transaction_method_str': 'multisig_simple', 'recipientAddress': '17RVTF3vJzsuaGh7a94DFkg4msJ7FcBYgX', 'padding': '000000', 'amount': '0000000002faf080', 'changeAddress': '182osbPxCo88oaSX4ReJwUr9uAcchmJVaL', 'formatted_amount': '0.50000000', 'baseCoin': '00', 'dataSequenceNum': '45', 'transactionType': '00000000'}
$
$ python msc_parse.py -t 298a6af50089184f7b434c700f83f390d5dfdd5dac10b39b95f99036a5c66df7
[I] main: {'currency_type_str': 'Test Mastercoin', 'transaction_type_str': 'Simple send', 'currencyId': '00000002', 'transaction_method_str': 'multisig_simple', 'recipientAddress': '17RVTF3vJzsuaGh7a94DFkg4msJ7FcBYgX', 'padding': '000000', 'amount': '0000000000000003', 'changeAddress': '182osbPxCo88oaSX4ReJwUr9uAcchmJVaL', 'formatted_amount': '0.00000003', 'baseCoin': '00', 'dataSequenceNum': '45', 'transactionType': '00000000'}
$
```

```
$ python msc_validate.py -h
Usage: msc_validate.py [options]

Options:
  -h, --help   show this help message and exit
  -d, --debug  turn debug mode on
```

enjoy!

BTC/Mastercoins Tips Jar:
* https://masterchain.info/Address.html?addr=182osbPxCo88oaSX4ReJwUr9uAcchmJVaL&currency=MSC



