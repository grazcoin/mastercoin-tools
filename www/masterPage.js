
function NavigationController($scope, $http) {
    $scope.values = {};

    var myURLParams = BTCUtils.getQueryStringArgs();
    var title = myURLParams['title'].toString();
    var currency = myURLParams['currency'].toString();
    $scope.title = title;
    $scope.currency = currency;
    $scope.footer = "FOOTER";
    $scope.getNavData = function () {

        $scope.values = {};
        // Make the http request and process the result
        $http.get('values.json', {}).success(function (data, status, headers, config) {

            $scope.values = data;
        });

    }
}

$(document).ready(function () {
    var footerHeight = $('footer').height();
    var headerHeight = $('header').height();
    var windowHeight = $(window).height();

    var maxContentHeight = windowHeight - footerHeight - headerHeight - 70;


    var contentHeight = $('.no-fixed').height();

    if (contentHeight < maxContentHeight) {
        $('.fixed').css('height', maxContentHeight);
    }
    else {
        $('.fixed').css('height', contentHeight);
    }

	
    $(window).resize(function () {

         var height = $(window).height() - footerHeight - headerHeight - 70;
      
         var inner = $('.inner').height();

        if(height > inner){

            $('.fixed').css('height', height);
        	
        }
   
     });
	 
});
