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
                                    <caption>Sell offer details</caption>
                                    <tbody>
                                        <tr>
                                            <td>Seller</td>
                                            <td><a ng-href="Address.html?addr={{transactionInformation.from_address}}&currency={{currency}}">{{transactionInformation.from_address}}</a></td>
                                        </tr>
                                        <tr>
                                            <td>Currency</td>
                                            <td>{{transactionInformation.currency_str}}</td>
                                        </tr>
                                        <tr>
                                            <td>Price per coin</td>
                                            <td><span class="pull-left">{{transactionInformation.formatted_price_per_coin}} &#3647;/{{currency}}</span>
                                                <button type="button" ng-click="AcceptClick()" class="pull-right btn btn-success btn-xs">ACCEPT</button></td>
                                        </tr>
                                        <tr>
                                            <td>Amount for sell</td>
                                            <td>{{transactionInformation.formatted_amount}}</td>
                                        </tr>
                                        <tr>
                                            <td>Amount available</td>
                                            <td>{{transactionInformation.formatted_amount_available}}</td>
                                        </tr>
                                        <tr>
                                            <td>Bitcoin amount desired</td>
                                            <td>{{transactionInformation.formatted_bitcoin_amount_desired}} &#3647;</td>
                                        </tr>
                                        <tr>
                                            <td>Fee required</td>
                                            <td>{{transactionInformation.formatted_fee_required}} &#3647;</td>
                                        </tr>
                                        <tr>
                                            <td>Payment timeframe (blocks)</td>
                                            <td>{{transactionInformation.formatted_block_time_limit}}</td>
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
												src="ico/selloffer24t.png"
												ng-init="createIconPopup()"
												data-content="{{transactionInformation.icon_text}}" rel="popover"
												data-placement="bottom"
												alt="" />
                                            {{transactionInformation.tx_type_str}}</td>
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
                                            <td class="{{transactionInformation.invalid|truefalsesearch}}ValidState"></td>
                                        </tr>
                                    </tbody>
                                </table>
                            </div>
                            <div class="clearfix"></div>
                            <div class="col-md-12">
                                <table class="table table-striped table-hover table-condensed">
                                    <caption>Bids on this offer</caption>
                                   <thead>
                                        <tr>
                                            <th>Transaction</th>
                                            <th>Amount</th>
                                            <th>Status</th>
                                            <th>Date</th>
                                        </tr>
                                   </thead>
                                    <tbody>
                                        <tr ng-repeat="bid in bids">
                                            <td ng-switch on="bid.icon">
                                            	<img class="round-corner {{bid.color}} iconPopupInit"
													src="ico/{{bid.icon}}24t.png"
													ng-init="createIconPopup()"
													data-content="{{bid.icon_text}}" rel="popover"
													data-placement="bottom"
													alt="" />
                                                <span ng-switch-when="selloffer">
                                                    <a ng-href='selloffer.html?tx={{bid.tx_hash}}&currency={{currency}}'>{{bid.tx_hash | characters:10}}
                                                    </a>
                                                </span>
                                                <span ng-switch-when="sellaccept">
                                                    <a ng-href='sellaccept.html?tx={{bid.tx_hash}}&currency={{currency}}'>{{bid.tx_hash | characters:10}}
                                                    </a>
                                                </span>
                                                <span ng-switch-when="unknown">
                                                    <a ng-href='btcpayment.html?tx={{bid.tx_hash}}&currency={{currency}}'>{{bid.tx_hash | characters:10}}
                                                    </a>
                                                </span>
                                                <span ng-switch-when="simplesend">
                                                    <a ng-href='transaction.html?tx={{bid.tx_hash}}&currency={{currency}}'>{{bid.tx_hash | characters:10}}
                                                    </a>
                                                </span>
                                                <span ng-switch-default>{{bid.tx_hash | characters:10}}
                                                </span>
                                            </td>


                                            <td>{{bid.formatted_amount}}</td>
                                            <td>{{bid.status}}</td>
                                            <td>{{bid.tx_time | date:'yyyy-MM-dd HH:mm:ss UTC'}}</td>
                                        </tr>
                                    </tbody>
                                </table>
                            </div>
                        </div>
                     </div>
                  </div>

