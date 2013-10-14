
function NavigationController($scope, $http) {
    $scope.values = {};

    var myURLParams = BTCUtils.getQueryStringArgs();
    var title = myURLParams['title'].toString();
    var currency = myURLParams['currency'].toString();
    $scope.title = title;
    $scope.currency = currency;
    $scope.footer = '';
    
    $scope.getNavData = function () {

        $scope.values = {};
        // Nav bar selection - Make the http request and process the result
        $http.get('values.json', {}).success(function (data, status, headers, config) {
           $scope.values = data;
	   angular.forEach($scope.values, function(value, key){
	    if (value.currency==$scope.currency)
		$scope.values[key].selected="selected";
	    else
		$scope.values[key].selected="";
	  });
        });
    }
}

function RevisionController($scope, $http) {
    $scope.revision = {};
    
    $scope.getData = function () {
        
        // Revision - Make the http request and process the result
	$http.get('revision.json', {}).success(function (data, status, headers, config) {
	    $scope.revision=data;
        });

    }
}

