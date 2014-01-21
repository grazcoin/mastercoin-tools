            <div class="container page-container">
                <div class="row">
                    <div class="no-fixed col-sm-9 col-sm-push-3 col-md-10 col-md-push-2">
                        <div class="AcceptOfferController" ng-controller="AcceptOfferController" ng-init="getSellofferData()">
                            <div class="col-md-6">
                                <h2>Accept sell offer
                                </h2>
                                <div class="input string optional" id="buyerAddressOrPublicKeyDiv">
                                    <!-- <div class="ui-widget">-->
                                    <label class="string optional" for="publicKey">Buyer address or public key</label>
                                    <select class="select optional form-control form-control30px combobox"
                                        id="buyerAddressOrPublicKey" name="buyerAddressOrPublicKey">
                                        <!-- ng-model="transactionInformation.to_address"
                                                ng-change="comboBoxValueChange(this)"-->
                                    </select>
                                    <!-- </div>
                                        <button id="toggle">Show underlying select</button>-->
                                    <div id="verify">
                                        <button id="verifyButton" class="btn btn-primary verifyButton">Verify</button>
                                        <p id="verifyMessage" class="verifyMessage"></p>
                                        <img id="verifyLoader" class="verifyLoader loader"
                                            src="img/ajax_loader.gif" />
                                    </div>
                                </div>
                                <div class="input string optional">
                                    <label class="string optional" for="amount">Amount</label>
                                    <input class="string optional form-control" id="amount"
                                        ng-model="transactionInformation.formatted_amount"
                                        ng-change="AmountChanged()"
                                        step="{{step}}"
                                        type="number">
                                    <p id="amountWarning" class="amountWarning">
                                        Exceeds sell offer
                                    </p>
                                </div>
                                <div class="input string optional">
                                    <label class="string optional" for="requiredFee">Price per coin</label>
                                    <input class="string optional form-control" readonly="readonly" id="pricePerCoin"
                                        ng-model="transactionInformation.formatted_price_per_coin" type="text">
                                </div>
                                <div class="input string optional">
                                    <label class="string optional" for="seller">Seller</label>
                                    <input class="string optional form-control" readonly="readonly" id="seller"
                                        ng-model="transactionInformation.from_address"
                                        type="text">
                                </div>
                                <div class="input string optional">
                                    <label class="string optional" for="currency">Currency</label>
                                    <input class="string optional form-control" readonly="readonly" id="currency"
                                        ng-model="transactionInformation.currency_str"
                                        type="text">
                                </div>
                                <div class="input string optional">
                                    <label class="string optional" for="requiredFee">Required fee</label>
                                    <input class="string optional form-control" readonly="readonly" id="requiredFee"
                                        ng-model="transactionInformation.formatted_fee_required" type="text">
                                </div>
                                <div>
                                    <button class="btn btn-primary btnMargin"
                                        id="createRawTransaction">
                                        Prepare
                                    </button>
                                    <img id="createRawTransactionLoader"
                                        src="img/ajax_loader.gif" class="loader" />
                                </div>
                            </div>
                            <!--AFTER RESPONSE-->
                            <div class="col-md-10" id="createRawResponseForm" style="display: none;">
                                <div class="input string optional">
                                    <label class="string optional" for="sourceScript">Source script</label>
                                    <textarea readonly="readonly" class="form-control textareaScroll" rows="3" id="sourceScript"></textarea>
                                </div>
                                <div class="input string optional">
                                    <label class="string optional" for="transactionBBE">Transaction</label>
                                    <textarea readonly="readonly" class="form-control textareaScroll" rows="6" id="transactionBBE"></textarea>
                                    <div id="rawJsonRadio" class="btn-group" data-toggle="buttons">
                                        <label id="RawRadioBtn" class="btn btn-primary active">
                                            <input type="radio" name="options">
                                            Raw
                                        </label>
                                        <label id="JsonRadioBtn" class="btn btn-primary">
                                            <input type="radio" name="options">
                                            Json
                                        </label>
                                    </div>
                                </div>
                                <div class="input string optional">
                                    <label class="string optional" for="privateKey">Private key</label>
                                    <input class="string optional form-control" id="privateKey"
                                        ng-model="key" ng-change="keyChange()"
                                        type="text">
                                    <span class="invalidKey redText">Invalid key</span>
                                </div>
                                <br />
                                <div>
                                    <button class="btn btn-primary btnMargin"
                                        id="reSign">
                                        (re)Sign
                                    </button>
                                    <img id="reSignLoader"
                                        src="img/ajax_loader.gif" class="loader" />
                                </div>
                            </div>
                            <div class="col-md-10" id="reSignClickedForm" style="display: none;">
                                <div class="input string optional">
                                    <label class="string optional" for="signedTransactionBBE">Transaction</label>
                                    <textarea class="form-control textareaScroll" rows="6" id="signedTransactionBBE"></textarea>
					<span class="invalidTransaction redText">Invalid transaction</span>
					<div id="rawJsonRadioSigned" class="btn-group" data-toggle="buttons">
					<label id="RawRadioBtnSigned" class="btn btn-primary active">
						<input type="radio" name="options">Raw
					</label>
					<label id="JsonRadioBtnSigned" class="btn btn-primary ">
						<input type="radio" name="options">Json
					</label>
                                    </div>
                                </div>
                                <div>
                                    <button class="btn btn-primary btnMargin"
                                        id="send">
                                        Send
                                    </button>
                                    <p id="sendMessage"  class="verifySendStatus"></p>
                                    <img id="sendLoader"
                                        src="img/ajax_loader.gif"
                                        class="loader" />
                                </div>
				<div id="sendHyperlink">
				    Check transaction: <a id="sendLink" href="#">Hyperlink</a>
                                </div>
                                <p></p>
                                <p></p>
                            </div>
                        </div>
                    </div>
