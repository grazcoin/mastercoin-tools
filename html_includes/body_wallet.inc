            <div class="container page-container" ng-controller="WalletController">
                <div class="row">
                    <div class="no-fixed col-sm-9 col-sm-push-3 col-md-10 col-md-push-2">
                        <div class="inner">
                            <div class="row">
				<div class="col-md-12">
					<table class="table table-striped table-hover table-condensed">
						<tr>
							<td>Wallet UUID:</td>
							<td><span class="pull-right">{{uuid}}</span></td>
						</tr>
						<tr>
							<td>Tools</td>
							<td class="btnCell">
							<button type="button" ng-click="CreateNewWallet()" class="btc-tbl-btn pull-right btn btn-success btn-xs">Create new wallet</button>
							<button type="button" class="btc-tbl-btn pull-right btn btn-success btn-xs">Sync with server</button>
							</td>
						</tr>
					</table>
				</div>
            		    </div>
                            <div class="row">
                                <div class="col-md-12">
                                    <table class="table table-condensed">
                                        <caption>Table of addresses</caption>
                                        <thead>
                                            <tr>
                                                <th>Address</th>
                                                <th ng-repeat="header in currencies">{{header.name}}</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            <tr ng-repeat="addr in addressArray">
                                                <td>
                                                    <button type="button" ng-click="DeleteAddress($index)" class="btc-tbl-btn btn btn-success btn-xs">X</button>
                                                    <a href="Address.html?addr={{addr.address}}">{{addr.address}}</a>
                                                </td>
                                                <td ng-repeat="balance in addr.balance">
                                                    <a href="sendform.html?addr=&amount={{balance}}&from={{addr.address}}&currency={{currencies[$index].symbol}}"><button type="button" class="btc-tbl-btn btn btn-success btn-xs">Send</button></a>
                                                    <a href="sellform.html?addr=&amount={{balance}}&from={{addr.address}}&currency={{currencies[$index].symbol}}"><button type="button" class="btc-tbl-btn btn btn-success btn-xs">Sell</button></a>
						    {{balance}}
						</td>
                                            </tr>
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        </div>
                    </div>
