#! /usr/bin/python 

from twython import Twython
import webbrowser


def webAuthentication():
    APP_KEY = 'b1WTyzKmLnG7KwnDcYpiQ'

    APP_SECRET = 'gzKci8Gys0i831zt7gPq3fEpG4qq9kgOINfbKhS8'

    twitter = Twython(APP_KEY, APP_SECRET)

    auth = twitter.get_authentication_tokens(callback_url='http://ignore.ninja-bounce-house.appspot.com/complete/')

    OAUTH_TOKEN = auth ['oauth_token']
    OAUTH_TOKEN_SECRET = auth['oauth_token_secret']

    return auth

    '''oauth_verifier = request.GET['oauth_verifier']

    twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)

    final_step = twitter.get_authorized_tokens(oauth_verifier)'''


def Authentication():
    APP_KEY = 'b1WTyzKmLnG7KwnDcYpiQ'

    APP_SECRET = 'gzKci8Gys0i831zt7gPq3fEpG4qq9kgOINfbKhS8'

    twitter = Twython(APP_KEY, APP_SECRET)

    auth = twitter.get_authentication_tokens()

    OAUTH_TOKEN = auth ['oauth_token']
    OAUTH_TOKEN_SECRET = auth['oauth_token_secret']

    webbrowser.open(auth['auth_url'])
    twitter =  Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)

    final_step = twitter.get_authorized_tokens(str(raw_input("Please enter the PIN: "))) #atm pin must be entered through the terminal

    OAUTH_TOKEN = final_step['oauth_token']
    OAUTH_TOKEN_SECRET = final_step['oauth_token_secret']

    print APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET

    twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)

    return twitter


def make_twit(Oauth1,Oauth2):
    APP_KEY = 'b1WTyzKmLnG7KwnDcYpiQ'

    APP_SECRET = 'gzKci8Gys0i831zt7gPq3fEpG4qq9kgOINfbKhS8'

    twitter = Twython(APP_KEY, APP_SECRET,Oauth1,Oauth2)

    return twitter

def Image_post(Usr_object): # the twitter usr
    photo = open('Tails.png', 'rb')
    Usr_object.update_status_with_media(status ='Ok now I can add images', media=photo)
    #Usr_object.update_status(status = 'First try')



