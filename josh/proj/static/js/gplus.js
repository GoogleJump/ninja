// Google+ sign-in button callback function
var authResult = undefined;

var twitter_connected = false;
var google_connected = false;
var facebook_connected = false;

function userConnected() {
	return (twitter_connected || google_connected || facebook_connected);
}

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
	var request = $.ajax({
		type: 'POST',
		url: window.location.href + 'connect-google',
		contentType: 'application/octet-stream; charset=utf-8',
		// prevents data from being transformed into a query string
		processData: false,
		data: this.authResult.code
	});

	request.done(function(result) {
		console.log(result);
		$('#connected').show();
		$('#google-connected').show();
		google_connected = true;
		displayUser();
	});

	request.fail(function(error) {
		console.log('error: ' + error);
	});
}

function disconnectGoogle() {
	// redisplay the sign-in button
	$('#google-connect').show('slow');
	$('#google-connected').hide('slow');

	var connected = userConnected();
	if (!connected) {
		$('#conntected').hide('slow');
	}

	var request = $.ajax({
		type: 'POST',
		url: window.location.href + 'disconnect-google',
		async: false
	});

	request.done(function(result) {
		console.log('revoke response: ' + result);
		google_connected = false;
	});

	request.fail(function(error) {
		console.log('error: ' + error);
	})
}

function displayUser() {
	var request = $.ajax({
		type: 'GET',
		url: window.location.href + 'google-user',
		async: false
	});

	request.done(function(result) {
		var name = result['displayName'];
		$('#user-name').text("Hi " + name + ". Now that you're signed in, choose an option below.");
	});

	request.fail(function(error) {
		console.log('error: ' + error);
	});
}

$(document).ready(function() {
	$('#google-disconnect').click(disconnectGoogle);
});