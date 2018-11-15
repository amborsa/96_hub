var var_update = setInterval(js_update, 5000);

function js_update() {
	req = $.ajax({
            url : '/update_main',
            type : 'POST'
        });

	req.done(function(data) {
			$('#1').fadeOut(1000).fadeIn(1000);
			$('#2').fadeOut(1000).fadeIn(1000);
        });

}

// var myVar = setInterval(myTimer, 1000);

// function myTimer() {
//     var d = new Date();
//     // document.getElementById("1").innerHTML = d.toLocaleTimeString();
//     document.getElementById("1").innerHTML = "live";
// }