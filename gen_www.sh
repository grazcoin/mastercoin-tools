#!/bin/sh
cd html_includes

FILE=../www/index.html
TITLE="Recent"
SCRIPT1="masterEvents.js"
cat	head_begin.inc > $FILE
echo "         $TITLE" >> $FILE
cat	head_middle.inc >> $FILE
echo "      <script src=\"$SCRIPT1\"></script>" >> $FILE
cat	head_end.inc \
	body_first.inc \
	body_nav.inc \
	body_recent.inc \
	body_paginator.inc \
	body_post_paginator.inc \
	body_last.inc >> $FILE

FILE=../www/Address.html
TITLE="Address information"
SCRIPT1="js/jquery.qrcode.min.js"
SCRIPT2="js/bootstrap.min.js"
SCRIPT3="address.js"
SCRIPT4="wallet.js"
cat	head_begin.inc > $FILE
echo "         $TITLE" >> $FILE
cat	head_middle.inc >> $FILE
echo "      <script src=\"$SCRIPT1\"></script>" >> $FILE
echo "      <script src=\"$SCRIPT2\"></script>" >> $FILE
echo "      <script src=\"$SCRIPT3\"></script>" >> $FILE
echo "      <script src=\"$SCRIPT4\"></script>" >> $FILE
cat	head_end.inc \
	body_first.inc \
	body_nav.inc \
	body_address.inc \
	body_last.inc >> $FILE


FILE=../www/simplesend.html
TITLE="Simple Send"
SCRIPT1="simplesend.js"
cat	head_begin.inc > $FILE
echo "         $TITLE" >> $FILE
cat	head_middle.inc >> $FILE
echo "      <script src=\"$SCRIPT1\"></script>" >> $FILE
cat	head_end.inc \
	body_tx_first.inc \
	body_nav.inc \
	body_simplesend.inc \
	body_last.inc >> $FILE

FILE=../www/exodus.html
TITLE="Exodus Transaction"
SCRIPT1="simplesend.js"
cat	head_begin.inc > $FILE
echo "         $TITLE" >> $FILE
cat	head_middle.inc >> $FILE
echo "      <script src=\"$SCRIPT1\"></script>" >> $FILE
cat	head_end.inc \
	body_tx_first.inc \
	body_nav.inc \
	body_simplesend.inc \
	body_last.inc >> $FILE

FILE=../www/selloffer.html
TITLE="Sell Offer"
SCRIPT1="selloffer.js"
cat	head_begin.inc > $FILE
echo "         $TITLE" >> $FILE
cat	head_middle.inc >> $FILE
echo "      <script src=\"$SCRIPT1\"></script>" >> $FILE
cat	head_end.inc \
	body_tx_first.inc \
	body_nav.inc \
	body_selloffer.inc \
	body_last.inc >> $FILE

FILE=../www/sellaccept.html
TITLE="Sell Accept"
SCRIPT1="sellaccept.js"
cat	head_begin.inc > $FILE
echo "         $TITLE" >> $FILE
cat	head_middle.inc >> $FILE
echo "      <script src=\"$SCRIPT1\"></script>" >> $FILE
cat	head_end.inc \
	body_tx_first.inc \
	body_nav.inc \
	body_sellaccept.inc \
	body_last.inc >> $FILE

FILE=../www/btcpayment.html
TITLE="Bitcoin Payment"
SCRIPT1="btcpayment.js"
cat	head_begin.inc > $FILE
echo "         $TITLE" >> $FILE
cat	head_middle.inc >> $FILE
echo "      <script src=\"$SCRIPT1\"></script>" >> $FILE
cat	head_end.inc \
	body_tx_first.inc \
	body_nav.inc \
	body_btcpayment.inc \
	body_last.inc >> $FILE

FILE=../www/sendform.html
TITLE="Send Coins"
LINK1="css/acceptform.css"
SCRIPT1="wallet.js"
SCRIPT2="sendform.js"
SCRIPT3="masterEvents.js"
SCRIPT4="js/BTCClientContext.js"
cat	head_begin.inc > $FILE
echo "         $TITLE" >> $FILE
cat	head_middle.inc >> $FILE
echo "      <link href=\"$LINK1\" rel=\"stylesheet\">" >> $FILE
echo "      <script src=\"$SCRIPT1\"></script>" >> $FILE
echo "      <script src=\"$SCRIPT2\"></script>" >> $FILE
echo "      <script src=\"$SCRIPT3\"></script>" >> $FILE
echo "      <script src=\"$SCRIPT4\"></script>" >> $FILE
cat	bitcoin.inc \
	head_end.inc \
	body_first.inc \
	body_nav.inc \
	body_sendform.inc \
	body_last.inc >> $FILE

FILE=../www/sellform.html
TITLE="Create Sell Offer"
LINK1="css/acceptform.css"
SCRIPT1="wallet.js"
SCRIPT2="sellform.js"
SCRIPT3="masterEvents.js"
SCRIPT4="js/BTCClientContext.js"
cat	head_begin.inc > $FILE
echo "         $TITLE" >> $FILE
cat	head_middle.inc >> $FILE
echo "      <link href=\"$LINK1\" rel=\"stylesheet\">" >> $FILE
echo "      <script src=\"$SCRIPT1\"></script>" >> $FILE
echo "      <script src=\"$SCRIPT2\"></script>" >> $FILE
echo "      <script src=\"$SCRIPT3\"></script>" >> $FILE
echo "      <script src=\"$SCRIPT4\"></script>" >> $FILE
cat	bitcoin.inc \
	head_end.inc \
	body_first.inc \
	body_nav.inc \
	body_sellform.inc \
	body_last.inc >> $FILE

FILE=../www/acceptform.html
TITLE="Accept Sell Offer"
LINK1="css/acceptform.css"
SCRIPT1="wallet.js"
SCRIPT2="acceptform.js"
SCRIPT3="masterEvents.js"
SCRIPT4="js/BTCClientContext.js"
cat	head_begin.inc > $FILE
echo "         $TITLE" >> $FILE
cat	head_middle.inc >> $FILE
echo "      <link href=\"$LINK1\" rel=\"stylesheet\">" >> $FILE
echo "      <script src=\"$SCRIPT1\"></script>" >> $FILE
echo "      <script src=\"$SCRIPT2\"></script>" >> $FILE
echo "      <script src=\"$SCRIPT3\"></script>" >> $FILE
echo "      <script src=\"$SCRIPT4\"></script>" >> $FILE
cat	bitcoin.inc \
	head_end.inc \
	body_first.inc \
	body_nav.inc \
	body_acceptform.inc \
	body_last.inc >> $FILE

FILE=../www/wallet.html
TITLE="Wallet"
SCRIPT1="wallet.js"
cat	head_begin.inc > $FILE
echo "         $TITLE" >> $FILE
cat	head_middle.inc >> $FILE
echo "      <script src=\"$SCRIPT1\"></script>" >> $FILE
cat	head_end.inc \
	body_first.inc \
	body_nav.inc \
	body_wallet.inc \
	body_last.inc >> $FILE


FILE=../www/404.html
TITLE="404"
cat	head_begin.inc > $FILE
echo "         $TITLE" >> $FILE
cat	head_middle.inc >> $FILE
cat	head_end.inc \
	body_first.inc \
	body_nav.inc \
	body_404.inc \
	body_last.inc >> $FILE

FILE=../www/About.html
TITLE="About"
cat	head_begin.inc > $FILE
echo "         $TITLE" >> $FILE
cat	head_middle.inc >> $FILE
cat	head_end.inc \
	body_first.inc \
	body_nav.inc \
	body_About.inc \
	body_last.inc >> $FILE

FILE=../www/API.html
TITLE="API"
cat	head_begin.inc > $FILE
echo "         $TITLE" >> $FILE
cat	head_middle.inc >> $FILE
cat	head_end.inc \
	body_first.inc \
	body_nav.inc \
	body_API.inc \
	body_last.inc >> $FILE

FILE=../www/License.html
TITLE="License"
cat	head_begin.inc > $FILE
echo "         $TITLE" >> $FILE
cat	head_middle.inc >> $FILE
cat	head_end.inc \
	body_first.inc \
	body_nav.inc \
	body_License.inc \
	body_last.inc >> $FILE

