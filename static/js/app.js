




function js_update() {
	req = $.ajax({
            url : '/update_main',
            type : 'POST',
        });

	req.done(function(data) {
			

        });


    var d = new Date();
    document.getElementById("demo").innerHTML = d.toLocaleTimeString();
}