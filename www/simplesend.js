function TransactionController($scope, $http) {
    $scope.transactionInformation;

    $scope.footer = "FOOTER";
    $scope.title = "TITLE";

    $scope.getTransactionData = function () {

        // parse tx from url parameters
        var myURLParams = BTCUtils.getQueryStringArgs();
        var file = 'tx/' + myURLParams['tx'] + '.json';
        // Make the http request and process the result
        $http.get(file, {}).success(function (data, status, headers, config) {
            $scope.transactionInformation = data[0];
        });
    }
}
