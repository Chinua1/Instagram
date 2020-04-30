from google.appengine.ext import ndb

class Post(ndb.Model):
    image_label= ndb.StringProperty()
    post_caption = ndb.StringProperty()
    created_at = ndb.DateTimeProperty()
    created_by = ndb.StringProperty()
