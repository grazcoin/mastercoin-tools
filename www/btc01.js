function BTCController($scope, $http) {

    // Scope members
    $scope.transactions = {};
    $scope.caption = '';
    
    $scope.getData = function () {
        // Clear scope members
        $scope.transactions = {};
        $scope.caption = 'Latest Mastercoin transactions';

        // Make the http request and process the result
	    $http.get(
	   'general/MSC_0000.json',
		 {
		   
		 }).success(function (data, status, headers, config) {
		 	$scope.transactions = data;
		});
	}
}

