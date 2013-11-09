function SellacceptController($scope, $http) {
    $scope.transactionInformation;
    $scope.offers;

    $scope.footer = "FOOTER";
    $scope.title = "TITLE";

    $scope.getSellacceptData = function () {

        // parse tx from url parameters
        var myURLParams = BTCUtils.getQueryStringArgs();
        var file = 'tx/' + myURLParams['tx'] + '.json';
        console.log(file);
        // Make the http request and process the result

        $http.get(file, {}).success(function (data, status, headers, config) {
            $scope.transactionInformation = data[0];
            console.log(data);
        });

       
        var offersURL = "offers/offer-";
        offersURL += myURLParams['tx'];
        offersURL += ".json";

        //console.log(bidsURL);

        $.get(offersURL, {}).success(function (data) {
            //  console.log(data);
            data = $.parseJSON(data);
            console.log(data);
            $scope.offers = data;
            $scope.apply();
        });

    }
}
