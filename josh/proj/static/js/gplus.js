// Google+ sign-in button callback function
var authResult = undefined;

function googleCallback(authResult) {
  if (authResult['access_token']) {     // the user is signed in

	// Hide the sign-in button
	$('#google-connect').hide('slow');

	this.authResult = authResult;
	connectGoogle();
  } else {
	console.log('Sign-in state: ' + authResult['error']);
  }
}

function connectGoogle() {
	// Ajax is a group of web development techniques used on the client-side
	// It creates asynchronous Web Applications 
	// They can send and retrieve data in background without interfering with the existing page
	$.ajax({
		type: 'POST',
		// the url to which the request is sent
		url: window.location.href + 'connect-google',
		// what is this?
		contentType: 'application/octet-stream; charset=utf-8',
		// a function to call if the request succeeds
		success: function(result) {                         
			console.log(result);
			$('#connected').show();
		},
		// prevents data from being transformed into a query string
		processData: false,
		// data to be sent to the server
		data: this.authResult.code
	});
}

function disconnectGoogle() {
	// redisplay the sign-in button
	$('#google-connect').show('slow');
	$('#connected').hide('slow');

	$.ajax({
		type: 'POST',
		url: window.location.href + 'disconnect-google',
		async: false,
		success: function(result) {
			console.log('revoke response: ' + result);
		},
		error: function(e) {
			console.log(e);
		}
	});
}

$(document).ready(function() {
	$('#google-disconnect').click(disconnectGoogle);
});