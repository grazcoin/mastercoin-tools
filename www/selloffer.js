function SellofferController($scope, $http) {
    $scope.transactionInformation;
    $scope.bids;

    $scope.footer = "FOOTER";
    $scope.title = "TITLE";

    $scope.getBidsData = function () {

    }

    $scope.getSellofferData = function () {

        // parse tx from url parameters
        var myURLParams = BTCUtils.getQueryStringArgs();
        var file = 'tx/' + myURLParams['tx'] + '.json';
        console.log(file);
        // Make the http request and process the result

        $http.get(file, {}).success(function (data, status, headers, config) {
            $scope.transactionInformation = data[0];
            console.log(data);
        });

        var bidsURL = "bids/bids-";
        bidsURL += myURLParams['tx'];
        bidsURL += ".json";

          $.get(bidsURL, {}).success(function (data) {
            //  console.log(data);
              data = $.parseJSON(data);
              //console.log(data);
              $scope.bids = data;
              $scope.apply();
              console.log($scope.bids);
          });
      
    }
}
