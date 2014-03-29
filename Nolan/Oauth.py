#! /usr/bin/python 

from twython import Twython
from requests import *

APP_KEY = 'b1WTyzKmLnG7KwnDcYpiQ'

APP_SECRET = 'gzKci8Gys0i831zt7gPq3fEpG4qq9kgOINfbKhS8'

twitter = Twython(APP_KEY, APP_SECRET)

auth = twitter.get_authentication_tokens()

OAUTH_TOKEN = auth ['oauth_token']
OAUTH_TOKEN_SECRET = auth['oauth_token_secret']

print auth['auth_url']


twitter =  Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)

final_step = twitter.get_authorized_tokens(str(raw_input("Please enter the PIN: ")))

OAUTH_TOKEN = final_step['oauth_token']
OAUTH_TOKEN_SECRET = final_step['oauth_token_secret']

print APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET

twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)

twitter.update_status(status= "Ok now I' am using Twython")
