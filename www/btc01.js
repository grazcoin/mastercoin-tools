function BTCController($scope, $http) {

    // Scope members
    $scope.transactions = {};
    $scope.caption = '';
    
    $scope.getData = function () {
        // Clear scope members
        $scope.transactions = {};
        $scope.caption = 'Latest Mastercoin transactions';
	// parse currency from url parameters
	var myURLParams = BTCUtils.getQueryStringArgs();
	var file =  'general/' + myURLParams['currency'] + '_0000.json';
        // Make the http request and process the result
	    $http.get(
	   file,
		 {
		   
		 }).success(function (data, status, headers, config) {
		 	$scope.transactions = data;
		});
	}
}

