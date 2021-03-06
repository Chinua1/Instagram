from google.appengine.ext import ndb
from post import Post

class User( ndb.Model ):
    firstname = ndb.StringProperty()
    lastname = ndb.StringProperty()
    username = ndb.StringProperty()
    email = ndb.StringProperty()
    profile_image = ndb.StringProperty()
    following = ndb.StringProperty(repeated = True)
    followers = ndb.StringProperty(repeated = True)
    posts = ndb.StringProperty(repeated = True)
