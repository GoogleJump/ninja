$(document).ready(function() {

	$('#upload-form').validate({

		rules: {
		    file: {
		      required: true,
		      extension: "jpg|jpeg|png"
		    }
		}
	});
	
});