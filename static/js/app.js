




function js_update() {
	req = $.ajax({
            url : '/update',
            type : 'POST',
        });




    var d = new Date();
    document.getElementById("demo").innerHTML = d.toLocaleTimeString();
}