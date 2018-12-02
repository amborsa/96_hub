// update upon starting the page
$(document).ready(function() {
    js_update()
});


// set to update every 1 second
// lkjlkjvar var_update = setInterval(js_update, 1000);

// function which calls for an update of alarm state
// IT WOULD BE GREAT IF WE COULD REQUEST ONLY WHEN THE USER IS ON "/" -- IS THIS POSSIBLE?
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
      console.log('does it get here?')
  });


  console.log('does it get here?')
  req1 = $.ajax({
            url : '/serial_listen',
            type : 'POST'
        });

  req1.done(function(data) {
      console.log('serial_listen completed')
  });

}

function plot() {

  // Testing out this other way to plot things...

  $.ajax({
      type: "POST",
      url: '/patient',
      data: {},
      success: function(data)
      {
          var tabData = JSON.parse(hr);
          var finals = [];
          for(var i = 0; i < tabData.length; i++)
          {
              var time = tabData[i].x;
              finals.push({ 'x': new time, 'y': tabData[i].y });
              // finals.push({ 'x': new Date(res[2],res[1],res[0]), 'y': tabData[i].count });
          }
          var chart = new CanvasJS.Chart("chartContainer",{
              title:{
                  text: "Patient Heart Rate"
              },
              data: [
                  {
                      type: "line",
                      dataPoints: finals
                  }
              ]
          });

          chart.render();
      }
  });
}
