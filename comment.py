from google.appengine.ext import ndb

class Comment(ndb.Model):
    text_body = ndb.StringProperty()
    created_at = ndb.DateTimeProperty()
    created_by = ndb.StringProperty()
