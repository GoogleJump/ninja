from proj import app

import httplib2, json, random, string

from flask import render_template, make_response, session, request, redirect, jsonify

from oauth2client.client import flow_from_clientsecrets, FlowExchangeError, AccessTokenCredentials, AccessTokenRefreshError, AccessTokenCredentialsError

from apiclient.discovery import build
from Oauth import *
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from werkzeug import parse_options_header

# read in the client_id from client_secrets.json
Client_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']

# create a service object to interact with an API
SERVICE = build('plus', 'v1')

app.secret_key = ''.join(random.choice(string.ascii_uppercase + string.digits)
                         for x in xrange(32))

APPLICATION_NAME = 'Bouncehouse'

#for twitter authentication
auth = 0

@app.route('/')
@app.route('/index')
def index():
    """ Render the homepage template """
    response = make_response(render_template("index.html", 
                                            TITLE = APPLICATION_NAME, 
                                            CLIENT_ID = Client_ID
                                            ))
    response.headers['Content-Type'] = 'text/html'
    return response

@app.route('/connect-google', methods=['POST'])
def connect():
    """Exchange the one-time authorization code for a token and store the token in the session."""
    
    # retrieve the one-time authorization code from the sign-in button
    code = request.data

    try:
        # create a flow object from client_secrets.json
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')

        # "postmessage" is a special flow for client-side authentication
        oauth_flow.redirect_uri = 'postmessage';

        # exchange authorization code for a credentials object, which holds refresh and access tokens
        credentials = oauth_flow.step2_exchange(code)

    except FlowExchangeError:
        response = make_response(json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # retrieve the gplus_id of the user
    gplus_id = credentials.id_token['sub']

    # retrieve existing user, if there is one
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

    response = make_response(json.dumps('Successfully connected user.'), 200)
    response.headers['Content-Type'] = 'application/json'
    return response

@app.route('/disconnect-google', methods=['POST'])
def disonnect():
    """ Disconnect a Google + user """

    # Only disconnect a connected user.
    user_agent = request.headers.get('User-Agent')
    credentials = AccessTokenCredentials(session.get('credentials'), user_agent)
    if credentials is None:
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # otherwise, get and revoke the access token
    access_token = credentials.access_token

    # make a request to revoke token URL
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
    """ Create a blobstore upload URL and render an upload form """
    # create an upload URL for the browser to upload a blob to
    # if the upload is successful, the user wil be rerouted to /upload
    upload_url = blobstore.create_upload_url('/upload')

    response = make_response(render_template("moment.html", 
                                            TITLE = APPLICATION_NAME, 
                                            ACTION = upload_url
                                            ))
    return response

@app.route('/upload', methods=['POST'])
def upload():
    """ Parse the form data for inserting a moment """

    title = request.form['title']
    msg = request.form['description']

    # retrieve the blob key for the uploaded file
    f = request.files['file']

    bkey = None

    if f is not None:
        # parse blob key from the incoming HTTP header
        header = f.headers['Content-Type']
        parsed_header = parse_options_header(header)
        bkey = parsed_header[1]['blob-key']

    return create_moment(title, bkey, msg)

@app.route('/create_moment', methods=['POST'])
def create_moment(title, blob_key, message):
    """ Insert a moment on a Google + user's profile """

    # check that the user is signed in
    user_agent = request.headers.get('User-Agent')
    credentials = AccessTokenCredentials(session.get('credentials'), user_agent)
    if credentials is None:
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    try:
        # authorize an instance of Http with a set of credentials
        http = httplib2.Http()
        http = credentials.authorize(http)

        if blob_key is not None:

            # create the url from which the image can be retrieved
            image_url = request.url_root + 'img/' + blob_key

            # create a moment with an image
            moment = {"type":"http://schemas.google.com/AddActivity",
                        "target": {
                            "id": "target-id-1",
                            "type":"http://schemas.google.com/AddActivity",
                            "name": title,
                            "description": message,
                            "image": image_url
                        }
                    }

        else:

            moment = {"type":"http://schemas.google.com/AddActivity",
                        "target": {
                            "id": "target-id-1",
                            "type":"http://schemas.google.com/AddActivity",
                            "name": title,
                            "description": message
                        }
                    }

        # insert the moment on the user's profile
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

@app.route('/img/<blob_key>')
def img(blob_key):
    """ Serve an uploaded image """

    blob_info = blobstore.get(blob_key)
    response = make_response(blob_info.open().read())
    response.headers['Content-Type'] = blob_info.content_type
    return response

@app.route('/google-user')
def getUser():
    user_agent = request.headers.get('User-Agent')
    credentials = AccessTokenCredentials(session.get('credentials'), user_agent)
    if credentials is None:
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    try:
        # authorize an instance of Http with a set of credentials
        http = httplib2.Http()
        http = credentials.authorize(http)
        people_resource = SERVICE.people()
        people_document = people_resource.get(userId='me').execute(http=http)
        return jsonify(people_document)

    except AccessTokenRefreshError:
        response = make_response(json.dumps('Failed to refresh access token.'), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    except AccessTokenCredentialsError:
        response = make_response(json.dumps('Access token is invalid or expired and cannot be refreshed.'), 500)
        response.headers['Content-Type'] = 'application/json'
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
