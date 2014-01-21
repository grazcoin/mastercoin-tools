            <div class="container page-container">
               <div class="row">
                  <div class="no-fixed col-sm-9 col-sm-push-3 col-md-10 col-md-push-2">
                     <div class="row">
                        <div class="col-md-12">
                           <table class="table table-striped table-hover table-condensed">
                              <tr>
                                 <td style="width:108px;"><strong>Transaction<strong></td>
                                 <td><span class="pull-right">{{transactionInformation.tx_hash}}</span></td>
                              </tr>
                           </table>
                        </div>
                     </div>
                     <div class="row">
                        <div class="transactionContainer">
                            <div class="col-md-6">
                                <table class="table table-striped table-hover table-condensed">
                                    <caption>Sell accept details</caption>
                                    <tbody>

                                        <tr>
                                            <td>Buyer</td>
                                            <td><a ng-href="Address.html?addr={{transactionInformation.from_address}}&currency={{currency}}">{{transactionInformation.from_address}}</a></td>
                                        </tr>
                                        <tr>
                                            <td>Seller</td>
                                            <td><a ng-href="Address.html?addr={{transactionInformation.to_address}}&currency={{currency}}">{{transactionInformation.to_address}}</a></td>
                                        </tr>
                                        <tr>
                                            <td>Currency</td>
                                            <td>{{transactionInformation.currency_str}}</td>
                                        </tr>
                                        <tr>
                                            <td>Price per coin</td>
                                            <td><span class="pull-left">{{transactionInformation.formatted_price_per_coin}} ฿/{{currency}}</span>
                                        </tr>
                                        <tr>
                                            <td>Amount requested</td>
                                            <td>{{transactionInformation.formatted_amount_requested}}</td>
                                        </tr>
                                        <tr>
                                            <td>Amount accepted</td>
                                            <td><span class="pull-left">{{transactionInformation.formatted_amount}}</span>
                                                <a href="sendform.html?addr={{transactionInformation.to_address}}&amount={{transactionInformation.bitcoin_required}}&from={{transactionInformation.from_address}}&currency=BTC&marker=True">
                                                     <button type="button" class="pull-right btc-tbl-btn btn btn-success btn-xs">PAY</button></a>
                                            </td>
                                        </tr>
                                        <tr>
                                            <td>Amount bought</td>
                                            <td>{{transactionInformation.formatted_amount_bought}}</td>
                                        </tr>
                                        <tr>
                                            <td>Status</td>
                                            <td>{{transactionInformation.status}}</td>
                                        </tr>
                                        <tr>
                                            <td>Bitcoin required</td>
                                            <td>{{transactionInformation.bitcoin_required}} ฿</td>
                                        </tr>
                                        <tr>
                                            <td>
                                            	<img class="round-corner {{sell_offer_tx.color}} iconPopupInit"
													src="ico/selloffer24t.png"
													ng-init="createIconPopup()"
													data-content="{{sell_offer_tx.icon_text}}" rel="popover"
													data-placement="bottom"
													alt="" />
                                            Sell Offer</td>
                                            <td><a ng-href="selloffer.html?tx={{transactionInformation.sell_offer_txid}}&currency={{currency}}">{{transactionInformation.sell_offer_txid|characters:10}}</a></td>
                                        </tr>
                                        <tr>
                                            <td>
                                            <img class="round-corner {{btc_payment.color}} iconPopupInit"
													src="ico/bitcoin24t.png"
													ng-init="createIconPopup()"
													data-content="{{btc_payment.icon_text}}" rel="popover"
													data-placement="bottom"
													alt="" />
                                            Payment</td>
                                            <td><a ng-href="btcpayment.html?tx={{transactionInformation.btc_offer_txid}}&currency={{currency}}">{{transactionInformation.btc_offer_txid|characters:10}}</a></td>
                                        </tr>

                                    </tbody>
                                </table>
                            </div>
                            <div class="col-md-6">
                                <table class="table table-striped table-hover table-condensed">
                                    <caption>Information</caption>
                                    <tbody>
                                        <tr>
                                            <td>Transaction type</td>
                                            <td>
                                            <img class="round-corner {{transactionInformation.color}} iconPopupInit"
												src="ico/sellaccept24t.png"
												ng-init="createIconPopup()"
												data-content="{{transactionInformation.icon_text}}" rel="popover"
												data-placement="bottom"
												alt="" />
                                             {{transactionInformation.tx_type_str}}</td>
                                        </tr>
                                        <tr>
                                            <td>Transaction ID</td>
                                            <td>{{transactionInformation.tx_hash|characters:30}}</td>
                                        </tr>
                                        <tr>
                                            <td>Included in block</td>
                                            <td>{{transactionInformation.block}}</td>
                                        </tr>
                                        <tr>
                                            <td>Index in block</td>
                                            <td>{{transactionInformation.index}}</td>
                                        </tr>
                                        <tr>
                                            <td>Block time</td>
                                            <td>{{transactionInformation.tx_time | date:'yyyy-MM-dd HH:mm:ss UTC'}}</td>
                                        </tr>
                                        <tr>
                                            <td>Transaction method</td>
                                            <td>{{transactionInformation.method}}</td>
                                        </tr>
                                        <tr>
                                            <td>Valid</td>
                                        	<td ng-switch on="transactionInformation.invalid|truefalsesearch" class="{{transactionInformation.invalid|truefalsesearch}}ValidStateDiv">
											  <div ng-switch-when="true" id="validPopup"
												  data-content="{{reason}}" rel="popover"
												  data-placement="bottom" data-original-title="Invalid"
												  ng-init="makePopup()">
												  Invalid
											  </div>
											  <div ng-switch-when="false">
												  Valid
											  </div>
                                       		</td>
                                        </tr>
                                    </tbody>
                                </table>
                            </div>
                        </div>
                     </div>
                  </div>
