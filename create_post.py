import webapp2
import jinja2
import os
import datetime

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

class CreatePost( webapp2.RequestHandler ):
    def get( self ):
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

        collection_key = ndb.Key( 'BlobCollection', 1)
        collection = collection_key.get()

        if collection == None:
            collection = BlobCollection( id = 1)
            collection.put()

        template_values = {
            "url": url,
            "logged_user": logged_user,
            "user": user,
            "firstname": firstname,
            "lastname": lastname,
            "username": username,
            "create_post_url": blobstore.create_upload_url( '/upload-request-handler' ),
            'has_params': has_params,
            'params_key': params_key,
            'params_value': params_value
        }
        template = JINJA_ENVIRONMENT.get_template( 'pages/create_post.html' )
        self.response.write( template.render( template_values ) )
        return
