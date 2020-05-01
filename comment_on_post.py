import webapp2
import jinja2
import os
import datetime
import json
import time

from google.appengine.api import users
from google.appengine.ext import ndb
from user import User
from comment import Comment

class AddCommentToPost( webapp2.RequestHandler ):
    def post( self, post_key ):
        self.response.headers[ 'Content-Type' ] = 'application/json'
        user = users.get_current_user()
        logged_user_key = ndb.Key( 'User', user.user_id() )
        logged_user = logged_user_key.get()
        comment = self.request.get( 'comment' )
        post = ndb.Key( 'Post', int(post_key) ).get()

        if comment and post:
            new_comment = Comment(
                text_body = comment,
                created_at = datetime.datetime.now(),
                created_by = str(logged_user.username).lower()
            )

            post.comments.append(new_comment)
            post.put()

        url = "/timeline#" + str(post.key.id())
        self.redirect(url)
