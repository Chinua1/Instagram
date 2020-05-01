from google.appengine.ext import ndb
from comment import Comment

class Post(ndb.Model):
    image_label= ndb.StringProperty()
    post_caption = ndb.StringProperty()
    created_at = ndb.DateTimeProperty()
    created_by = ndb.StringProperty()
    comments = ndb.StructuredProperty(Comment, repeated = True)
