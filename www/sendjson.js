
$(document).ready(function myfunction() {


    $('#sendjson').click(function () {
        $('#jsonresponse').val('');
        var urival = $('#urldata').val();
        var jsnval = $('#jsondata').val();
        var objval = jsnval;
        try {
		objval = JSON.parse(jsnval);
		}
		catch(err){ $('#jsonresponse').val(err); return;}
        $.post(urival, objval, function (data) {
            console.log('success');
            console.log(data);
            var str = JSON.stringify(data);
            $('#jsonresponse').val(str);
        }).fail(function () {
            $('#jsonresponse').val('HTTP Post failed (some error code from server, use chrome dev tools)');
        });
    });
    
});