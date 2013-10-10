function BTCController($scope, $http) {

    // Scope members
    $scope.transactions = {};
    $scope.caption = '';
    
    $scope.getData = function () {
        // Clear scope members
        $scope.transactions = {};
        $scope.caption = '';

        // Make the http request and process the result
	    $http.get(
	   'general/msc_tx_0000.json',
		 {
		   
		 }).success(function (data, status, headers, config) {
		 	$scope.transactions = data;
		});
	}
}

