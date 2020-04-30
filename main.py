import webapp2
import jinja2
import os
import datetime

from google.appengine.api import users
from google.appengine.ext import ndb

from user import User

from redirect_to_timeline import RedirectToTimelinePage
from user_profile import LoggedUserProfilePage
from user_profile_edit import LoggedUserProfileEditPage
from create_post import CreatePost
from upload_handler import UploadHandler
from selected_user_profile import SelectedUserProfilePage
from search_user import SearchPage
from api_request import APIServices

start = os.path.dirname( __file__ )
rel_path = os.path.join(start, 'templates')
abs_path = os.path.realpath(rel_path)

JINJA_ENVIRONMENT = jinja2.Environment(
    loader = jinja2.FileSystemLoader( abs_path ),
    extensions = [ 'jinja2.ext.autoescape' ],
    autoescape = True
)

class TimelinePage( webapp2.RequestHandler ):
    def get( self ):
        self.response.headers[ 'Content-Type' ] = 'text/html'

        url = ''
        logged_user = None
        user = users.get_current_user()
        firstname = ''
        lastname = ''
        username = ''

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
                    lastname = str(logged_user.lastname).capitalize()
                    firstname = str(logged_user.firstname).capitalize()
                    username = str(logged_user.username).lower()
                else:
                    temp_url = "/edit-profile"
                    self.redirect(temp_url)
                    return
        else:
            url = users.create_login_url( self.request.uri )
            self.redirect( url )
            return

        template_values = {
            "url": url,
            "logged_user": logged_user,
            "user": user,
            "firstname": firstname,
            "lastname": lastname,
            "username": username
        }

        template = JINJA_ENVIRONMENT.get_template( 'pages/index.html' )
        self.response.write( template.render( template_values ) )
        return

    def getLoggerUserFullname( self, lastname, firstname ):
        return firstname + " " + lastname

app = webapp2.WSGIApplication(
    [
        webapp2.Route( r'/api-request-resources', handler=APIServices, name='api-request-resources'),
        webapp2.Route( r'/search', handler=SearchPage, name='search-request-handler'),
        webapp2.Route( r'/upload-request-handler', handler=UploadHandler, name='upload-request-handler'),
        webapp2.Route( r'/create-post', handler=CreatePost, name='create-post'),
        webapp2.Route( r'/edit-profile', handler=LoggedUserProfileEditPage, name='edit-user-profile'),
        webapp2.Route( r'/<user_key:[^/]+>/profile', handler=SelectedUserProfilePage, name='selected-user-profile'),
        webapp2.Route( r'/profile', handler=LoggedUserProfilePage, name='user-profile'),
        webapp2.Route( r'/timeline', handler=TimelinePage, name='timeline'),
        webapp2.Route( r'/', handler=RedirectToTimelinePage, name='redirect-to-timeline'),
    ], debug = True
)
