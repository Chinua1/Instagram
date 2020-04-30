import webapp2
import jinja2
import os
import datetime

from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.ext import blobstore
from google.appengine.api import images

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

class LoggedUserProfileEditPage( webapp2.RequestHandler ):
    def get( self ):
        self.response.headers[ 'Content-Type' ] = 'text/html'
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
            if 'failed' in self.request.GET or 'lastname' in self.request.GET or 'firstname' in self.request.GET or 'username' in self.request.GET:
                has_params = True
                params_key = 'failed'
                firstname = self.request.params.get('firstname')
                lastname = self.request.params.get('lastname')
                username = self.request.params.get('username')
                params_value = self.request.params.get(params_key)
        except:
            pass

        if user:
            url = users.create_logout_url( self.request.uri )
            logged_user_key = ndb.Key( 'User', user.user_id() )
            logged_user = logged_user_key.get()

            if logged_user:
                if logged_user.firstname:
                    lastname = str(logged_user.lastname).capitalize()
                    firstname = str(logged_user.firstname).capitalize()
                    username = str(logged_user.username).lower()
        else:
            url = users.create_login_url( self.request.uri )
            self.redirect( url )
            return

        collection_key = ndb.Key( 'BlobCollection', 1 )
        collection = collection_key.get()


        if collection == None:
            collection = BlobCollection( id = 1)
            collection.put()

        template_values = {
            "url": url,
            "logged_user": logged_user,
            "profile_image_url": self.getProfileImage( logged_user, collection, images ),
            "user": user,
            "firstname": firstname,
            "lastname": lastname,
            "username": username,
            "has_params": has_params,
            "params_key": params_key,
            "params_value": params_value,
            "edit_user_profile_url": blobstore.create_upload_url( '/upload-request-handler' ),
        }
        template = JINJA_ENVIRONMENT.get_template( 'pages/edit_profile.html' )
        self.response.write( template.render( template_values ) )
        return

    def getProfileImage( self, logged_user, collection, images ):
        if not logged_user:
            return "https://image.flaticon.com/icons/png/512/23/23228.png"

        image_name = logged_user.profile_image
        try:
            index = collection.filenames.index(image_name)
            blob_key = collection.blobs[index]
            return images.get_serving_url(blob_key, secure_url=False)
        except:
            return "https://image.flaticon.com/icons/png/512/23/23228.png"
