from google.appengine.ext import ndb


class logggedin(ndb.Model):
	userid = ndb.StringProperty()
	twitter_key1 = ndb.StringProperty()
	twitter_key2 = ndb.StringProperty()

"""Example = logggedin(
    userid='Hey Trail',
    twitter_key1='SOme Randmo Dac',
    twitter_key2='SOme Randmo Dac'
)

Example.put()"""

