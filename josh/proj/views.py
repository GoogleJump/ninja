# import the variable app from the python package proj
from proj import app
from flask import render_template
from flask import make_response

# a session object allows the app to store information specific to a user from one request to another
from flask import session
# used to parse incoming request data; provides access through the global request object
from flask import request

from flask import redirect

# OAuth 2.0 steps require your application to potentially redirect a browser multiple times. 
# A Flow object has functions that help the application take these steps and acquire credentials.
from oauth2client.client import flow_from_clientsecrets
# an error trying to exchange an authorization grant for an access token
from oauth2client.client import FlowExchangeError
from oauth2client.client import AccessTokenCredentials
# an error trying to refresh an expired access token
from oauth2client.client import AccessTokenRefreshError

from oauth2client.client import AccessTokenCredentialsError

from apiclient.discovery import build
from Oauth import *
# a comprehensive HTTP client library
import httplib2

# An API to serve large data objects, blobs.
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers

from werkzeug import parse_options_header

import json
import random
import string

# set the application name to be filled in on a template
APPLICATION_NAME = 'Bouncehouse'

# read in the client_id from client_secrets.json
Client_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']

# create a service object to interact with an API
SERVICE = build('plus', 'v1')

app.secret_key = ''.join(random.choice(string.ascii_uppercase + string.digits)
                         for x in xrange(32))

#for twitter authentication
auth = 0

# map the urls '/' and '/index' to this function
@app.route('/')
@app.route('/index')
def index():
	# render_template is a Flask function that takes a template name and a list of arguments
	# it returns the rendered template, substituting {{}} blocks with corresponding values
	# make_response is a Flask function that converts a view functoin to a response object
	response = make_response(render_template("index.html", 
											TITLE = APPLICATION_NAME, 
											CLIENT_ID = Client_ID
											))
	response.headers['Content-Type'] = 'text/html'
	return response

# access the URL with the POST method, enabling the browser to post new information
@app.route('/connect-google', methods=['POST'])
def connect():
	"""Exchange the one-time authorization code for a token and store the token in the session."""
	code = request.data

	try:
		# create a flow object from client_secrets.json
		oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')

		# once the oauth has gone through, go to the postmessage endpoint
		oauth_flow.redirect_uri = 'postmessage';

		# exchange authorization code for a credentials object
		# a credentials object holds refresh and access tokens
		credentials = oauth_flow.step2_exchange(code)

	except FlowExchangeError:
		response = make_response(json.dumps('Failed to upgrade the authorization code.'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response

	# if successful, retrieve the identity of the resource owner
	# retrieve the gplus_id
	gplus_id = credentials.id_token['sub']
	stored_credentials = session.get('credentials')
	stored_gplus_id = session.get('gplus_id')

	# if the user is already connected
	if stored_credentials is not None and gplus_id == stored_gplus_id:
		response = make_response(json.dumps('Current user is already connected.'), 200)
		response.headers['Content-Type'] = 'application/json'
		return response

	# otherwise, store the information
	session['credentials'] = credentials.access_token
	session['gplus_id'] = gplus_id

	# json.dumps takes a Python data structure and returns it as a JSON string
	response = make_response(json.dumps('Successfully connected user.'), 200)
	response.headers['Content-Type'] = 'application/json'
	return response

@app.route('/disconnect-google', methods=['POST'])
def disonnect():
	# Only disconnect a connected user.
	user_agent = request.headers.get('User-Agent')
	credentials = AccessTokenCredentials(session.get('credentials'), user_agent)
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

@app.route('/moment', methods=['GET'])
def moment():
	# create an upload URL for the browser to upload a blob to
	# if success, reroute to /upload after uploading to blobstore
	upload_url = blobstore.create_upload_url('/upload')

	response = make_response(render_template("moment.html", 
											TITLE = APPLICATION_NAME, 
											ACTION = upload_url
											))
	return response

@app.route('/create_moment', methods=['POST'])
def create_moment(title, blob_key, message):
	user_agent = request.headers.get('User-Agent')
	credentials = AccessTokenCredentials(session.get('credentials'), user_agent)
	if credentials is None:
		response = make_response(json.dumps('Current user not connected.'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response


	try:
		http = httplib2.Http()
		# authorize an instance of Http with a set of credentials
		http = credentials.authorize(http)

		# create image_url
		image_url = request.url_root + 'img/' + blob_key

		# create a moment
		moment = {"type":"http://schemas.google.com/AddActivity",
					"target": {
						"id": "target-id-1",
						"type":"http://schemas.google.com/AddActivity",
						"name": title,
						"description": message,
						"image": image_url
					}
				}

		google_request = SERVICE.moments().insert(userId='me', collection='vault', body=moment)
		result = google_request.execute(http=http)
		response = make_response(render_template("uploaded.html"))
		response.headers['Content-Type'] = 'text/html'
		return response
	except AccessTokenRefreshError:
		response = make_response(json.dumps('Failed to refresh access token.'), 500)
		response.headers['Content-Type'] = 'application/json'
		return response
	except AccessTokenCredentialsError:
		response = make_response(json.dumps('Access token is invalid or expired and cannot be refreshed.'), 500)
		response.headers['Content-Type'] = 'application/json'
		return response

@app.route('/upload', methods=['POST'])
def upload():
	# retrieve the blob key for the uploaded file
	f = request.files['file']

	header = f.headers['Content-Type']
	parsed_header = parse_options_header(header)
	bkey = parsed_header[1]['blob-key']

	# retrieve the title
	title = request.form['title']

	if title == '':
		return redirect('/moment')

	# retrieve the text message
	msg = request.form['description']

	return create_moment(title, bkey, msg)

@app.route('/img/<blob_key>')
def img(blob_key):
	""" Serve an uploaded image """

	blob_info = blobstore.get(blob_key)
	response = make_response(blob_info.open().read())
	response.headers['Content-Type'] = blob_info.content_type
	return response

@app.route('/twit/')
def First_Part():
    global auth
    auth = webAuthentication()
    return redirect(str(auth['auth_url']))

@app.route('/complete/')
def Second_Part():
    global auth
    APP_KEY = 'b1WTyzKmLnG7KwnDcYpiQ'

    APP_SECRET = 'gzKci8Gys0i831zt7gPq3fEpG4qq9kgOINfbKhS8'

    oauth_verifier = request.args['oauth_verifier']

    twitter = Twython(APP_KEY, APP_SECRET, auth['oauth_token'], auth['oauth_token_secret'])

    final_step = twitter.get_authorized_tokens(oauth_verifier)

    return "all good"
