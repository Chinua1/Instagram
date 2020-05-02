import webapp2
import jinja2
import os
import datetime
import json

from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.ext import blobstore

from user import User
from blob_collection import BlobCollection

start = os.path.dirname( __file__ )
rel_path = os.path.join(start, 'templates')
abs_path = os.path.realpath(rel_path)

JINJA_ENVIRONMENT = jinja2.Environment(
    loader = jinja2.FileSystemLoader( abs_path ),
    extensions = [ 'jinja2.ext.autoescape' ],
    autoescape = True
)

class ViewAllCommentsOnAPostPage( webapp2.RequestHandler ):
    def get( self, post_key ):
        url = ''
        logged_user = None
        user = users.get_current_user()
        firstname = ''
        lastname = ''
        username = ''
        has_params = False
        params_key = ''
        params_value = ''

        try:
            if 'failed' in self.request.GET:
                has_params = True
                params_key = 'failed'
                params_value = self.request.get(params_key)
        except:
            pass

        if user:
            url = users.create_logout_url( self.request.uri )

            logged_user_key = ndb.Key( 'User', user.user_id() )
            logged_user = logged_user_key.get()

            if logged_user == None:
                logged_user = User( id = user.user_id() )
                logged_user.put()
                temp_url = "/edit-profile"
                self.redirect(temp_url)
                return
            else:
                if logged_user.firstname:
                    lastname = logged_user.lastname
                    firstname = logged_user.firstname
                    username = logged_user.username
                else:
                    temp_url = "/edit-profile"
                    self.redirect(temp_url)
                    return
        else:
            url = users.create_login_url( self.request.uri )
            self.redirect( url )
            return

        post = ndb.Key( 'Post', int(post_key) ).get()

        template_values = {
            "logged_user": logged_user,
            "user": user,
            "firstname": firstname,
            "lastname": lastname,
            "username": username,
            "comments": self.sortPosts(post.comments),
            "post": post
        }
        template = JINJA_ENVIRONMENT.get_template( 'pages/view_all_comment.html' )
        self.response.write( template.render( template_values ) )
        return

    def sortPosts(self, posts):
        for i in range(1, len(posts)):
            j = i-1
            nxt_element = posts[i]
            while (posts[j].created_at < nxt_element.created_at) and (j >= 0):
                posts[j+1] = posts[j]
                j=j-1
            posts[j+1] = nxt_element
        return posts
