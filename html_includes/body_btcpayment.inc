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
                                    <caption>Bitcoin payment details</caption>
                                    <tbody>
                                        <tr>
                                            <td>From</td>
                                            <td><a ng-href="Address.html?addr={{transactionInformation.from_address}}&currency={{currency}}">{{transactionInformation.from_address}}</a></td>
                                        </tr>
                                        <tr ng-repeat="f in transactionInformation.to_address">
                                            <td>
                                                <span class="pull-left">To <a href="Address.html?addr={{f.address}}">{{f.address | characters:10}}</a></span>
                                            </td>
                                            <td>
                                                <span class="pull-right">{{f.value}} ฿</span>
                                                </td>
                                        </tr>
                                        <tr>
                                            <td>Currency</td>
                                            <td><span class="pull-right">Bitcoin</span></td>
                                        </tr>
                                        <tr>
                                            <td>Fee</td>
                                            <td><span class="pull-right">{{transactionInformation.fee}} ฿</span></td>
                                        </tr>
                                        <tr>
                                            <td>Sell Offer</td>
                                            <td><a href="selloffer.html?tx={{transactionInformation.sell_offer_txid}}">{{transactionInformation.sell_offer_txid}}</a></td>
                                        </tr>
                                        <tr>
                                            <td>Accept Offer</td>
                                            <td><a href="sellaccept.html?tx={{transactionInformation.accept_txid}}">{{transactionInformation.accept_txid}}</a></td>
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
												src="ico/bitcoin24t.png"
												ng-init="createIconPopup()"
												data-content="{{transactionInformation.icon_text}}" rel="popover"
												data-placement="bottom"
												alt="" />
                                            Bitcoin payment</td>
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
                                    </tbody>
                                </table>
                            </div>
                        </div>
                     </div>
                  </div>
