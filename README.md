mastercoin-tools
================

Package of mastercoin related tools.
The intention is to help finalizing the spec, and enable easy further coding.
It is based on https://github.com/spesmilo/sx with minor fixes on 
https://github.com/grazcoin/sx

For finalizing the spec, a list of address and mastercoins is generated.

To get all mastercoins sells during exodus bootstrap in csv format:
python msc_bootstrap.py > outputs/bootstrap.log

To get total amount of mastercoins for each address:
python bootstrap_msc_per_address.py > outputs/msc_per_address.csv

To get the whole bootstrap story (for fun and debug), check:
python msc_bootstrap.py story > outputs/bootstrap_story.log

The outputs of those scripts are available under outputs directory.

Once this list is agreed on the community, it would be possible to sign it
with 1EXoDus address and take it as appendix for the spec (best would be
as part of the github repository of the ascii spec).
Also future protocol stack implementations could use it.


Aim of this package:

1. Live update - direct interaction with the bitcoin network (using sx monitor).

2. Run without a database.

3. Be an alternative code base.


Anyone should be able to run at home without the need for a database setup.

Next steps:

1. Parse mastercoin tx for all tx coming from sx-monitor tool listening on 1EXoDus address creating a mastercoin tx log (dropping the syntax invalid tx).

2. Accounting validator - checks that enough funds are available for each tx. Insufficient funds would mean invalid tx.


enjoy!

BTC/Mastercoins Tips Jar:
182osbPxCo88oaSX4ReJwUr9uAcchmJVaL
