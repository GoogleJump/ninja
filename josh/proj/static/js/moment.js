$(document).ready(function() {

	$('#upload-form').validate({

		rules: {
		    file: {
		      extension: "jpg|jpeg|png"
		    }
		}
	});
	
});