function TransactionController($scope, $http) {
    $scope.transactionInformation;
    $scope.bids;
    $scope.footer = "FOOTER";
    $scope.title = "TITLE";
    $scope.reason = "unknown";

    $scope.createIconPopup = function () {
        $('.iconPopupInit').popover({ trigger: "hover" });           
    };

    //Function for creating popup
    $scope.makePopup = function () {
	//Popup for valid/invalid 
	$('#validPopup').popover({ trigger: "hover" });
	var navHeight = $('.navbar').height();
	$('.page-container').css('paddingTop', navHeight + 20);
    };
    
    $scope.getTransactionData = function () {

        // parse tx from url parameters
        var myURLParams = BTCUtils.getQueryStringArgs();
        var file = 'tx/' + myURLParams['tx'] + '.json';
        // Make the http request and process the result
        $http.get(file, {}).success(function (data, status, headers, config) {
            $scope.transactionInformation = data[0];
            $scope.updateReason();
        });

        var bidsURL = "bids/bids-";
        bidsURL += myURLParams['tx'];
        bidsURL += ".json";

          $.get(bidsURL, {}).success(function (data) {
              //data = $.parseJSON(data);
              $scope.bids = data;
              $scope.$apply();
          });
      
    }

    $scope.AcceptClick = function () {
        var myURLParams = BTCUtils.getQueryStringArgs();
        var url = "acceptform.html?tx=";
        url += myURLParams['tx'];
        window.location = url;
    }
    $scope.updateReason = function () {
        if (!angular.isArray($scope.transactionInformation.invalid)) return;
        if ($scope.transactionInformation.invalid.length < 2) return;
        $scope.reason = $scope.transactionInformation.invalid[1];
    }
}
