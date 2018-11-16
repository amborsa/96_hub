$(document).onopen(function() {
	js_update()
});


// set to update every 5 seconds
var var_update = setInterval(js_update, 5000);

// function which calls for an update of alarm state
function js_update() {
	// sends request to /update_main
	req = $.ajax({
            url : '/update_main',
            type : 'POST'
        });

	// receives response from /update_main
	req.done(function(data) {
			var i;
			for (i=0; i < data.length; i++) {
				if (data[i].alarm_state == true) {
					$('#alarm_state' + data[i].id).css({
						backgroundColor: '#d62728'
					});
				} else {
					$('#alarm_state' + data[i].id).css({
						backgroundColor: 'white'
					});
				}
			}
        })
}