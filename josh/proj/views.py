# import the variable app from the python package proj
from proj import app
from flask import render_template
from flask import make_response

# a session object allows the app to store information specific to a user from one request to another
from flask import session
# used to parse incoming request data; provides access through the global request object
from flask import request

# OAuth 2.0 steps require your application to potentially redirect a browser multiple times. 
# A Flow object has functions that help the application take these steps and acquire credentials.
from oauth2client.client import flow_from_clientsecrets
# an error trying to exchange an authorization grant for an access token
from oauth2client.client import FlowExchangeError
# an error trying to refresh an expired access token
from oauth2client.client import AccessTokenRefreshError

from apiclient.discovery import build

# a comprehensive HTTP client library
import httplib2

import json
import random
import string

# set the application name to be filled in on a template
APPLICATION_NAME = 'Bouncehouse'

# read in the client_id from client_secrets.json
Client_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']

# create a service object to interact with an API
SERVICE = build('plus', 'v1')

# what is this?
app.secret_key = ''.join(random.choice(string.ascii_uppercase + string.digits)
                         for x in xrange(32))

# map the urls '/' and '/index' to this function
@app.route('/')
@app.route('/index')
def index():
	# render_template is a Flask function that takes a template name and a list of arguments
	# it returns the rendered template, substituting {{}} blocks with corresponding values
	# make_response is a Flask function that converts a view functoin to a response object
	response = make_response(render_template("index.html", 
											TITLE = APPLICATION_NAME, 
											CLIENT_ID= Client_ID
											#STATE = state
											))
	response.headers['Content-Type'] = 'text/html'
	return response

# access the URL with the POST method, enabling the browser to post new information
@app.route('/connect', methods=['POST'])
def connect():
	"""Exchange the one-time authorization code for a token and store the token in the session."""
	code = request.data

	try:
		# create a flow object from client_secrets.json
		oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')

		# what is this?
		oauth_flow.redirect_uri = 'postmessage';

		# exchange authorization code for a credentials object
		# a credentials object holds refresh and access tokens
		credentials = oauth_flow.step2_exchange(code)

	except FlowExchangeError:
	    response = make_response(json.dumps('Failed to upgrade the authorization code.'), 401)
	    response.headers['Content-Type'] = 'application/json'
	    return response

	# if successful, retrieve the identity of the resource owner
	# what is sub?
	gplus_id = credentials.id_token['sub']
	stored_credentials = session.get('credentials')
	stored_gplus_id = session.get('gplus_id')

	# if the user is already connected
	if stored_credentials is not None and gplus_id == stored_gplus_id:
		response = make_response(json.dumps('Current user is already connected.'),
		                         200)
		response.headers['Content-Type'] = 'application/json'
		return response

	# otherwise, store the information
	session['credentials'] = credentials
	session['gplus_id'] = gplus_id

	# json.dumps takes a Python data structure and returns it as a JSON string
	response = make_response(json.dumps('Successfully connected user.', 200))
	response.headers['Content-Type'] = 'application/json'

	return response

@app.route('/disconnect', methods=['POST'])
def disonnect():
	# Only disconnect a connected user.
	credentials = session.get('credentials')
	if credentials is None:
		response = make_response(json.dumps('Current user not connected.'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response

	# otherwise, get and revoke the access token
	access_token = credentials.access_token

	# make a request to this url to revoke a token
	url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token

	h = httplib2.Http()
	result = h.request(url, 'GET')[0]

	# if the revocation is successfully processed
	if result['status'] == '200':
		# Reset the user's session.
		del session['credentials']
		response = make_response(json.dumps('Successfully disconnected.'), 200)
		response.headers['Content-Type'] = 'application/json'
		return response

@app.route('/moment', methods=['POST'])
def moment():
	credentials = session.get('credentials')
	if credentials is None:
		response = make_response(json.dumps('Current user not connected.'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response
	try:
		http = httplib2.Http()
		# authorize an instance of Http with a set of credentials
		http = credentials.authorize(http)

		# create a moment
		moment = {"type":"http://schemas.google.com/AddActivity",
		        "target": {
		          "id": "target-id-1",
		          "type":"http://schemas.google.com/AddActivity",
		          "name": "The Google+ Platform",
		          "description": "A page that describes just how awesome Google+ is!",
		          "image": "https://developers.google.com/+/plugins/snippet/examples/thing.png"
		        }
		     }

		google_request = SERVICE.moments().insert(userId='me', collection='vault', body=moment)
		result = google_request.execute(http=http)
		response = make_response(json.dumps(result), 200)
		response.headers['Content-Type'] = 'application/json'
		return response
	except AccessTokenRefreshError:
		response = make_response(json.dumps('Failed to refresh access token.'), 500)
		response.headers['Content-Type'] = 'application/json'
		return response