import webapp2
import jinja2
import os
import datetime

from google.appengine.api import users
from google.appengine.ext import ndb

from user import User

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
            if 'lastname' in self.request.GET or 'firstname' in self.request.GET or 'username' in self.request.GET:
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
            "username": username,
            "has_params": has_params,
            "params_key": params_key,
            "params_value": params_value
        }
        template = JINJA_ENVIRONMENT.get_template( 'pages/edit_profile.html' )
        self.response.write( template.render( template_values ) )
        return

    def post( self ):
        self.response.headers[ 'Content-Type' ] = 'text/html'
        user = users.get_current_user()
        logged_user_key = ndb.Key( 'User', user.user_id() )
        logged_user = logged_user_key.get()
        lastname = self.request.get('lastname')
        firstname = self.request.get('firstname')
        username = self.request.get('username')

        if lastname == '' or firstname == '' or username == '':
            message = 'Please fill out all fields'
            query_string = '?failed=' + message + '&lastname=' + lastname + '&firstname=' + firstname + '&username=' + username
            url = '/edit-profile' + query_string
            self.redirect( url)
            return
        else:
            logged_user.lastname = lastname
            logged_user.firstname = firstname
            logged_user.username = username
            logged_user.email = user.email()
            logged_user.put()
            url = '/profile'
            self.redirect( url)
            return
