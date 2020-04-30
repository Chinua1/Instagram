import webapp2
import jinja2
import os
import datetime
import json
import time

from google.appengine.api import users
from google.appengine.ext import ndb
from user import User

class APIServices( webapp2.RequestHandler ):
    def post( self ):
        self.response.headers[ 'Content-Type' ] = 'application/json'
        user = users.get_current_user()
        logged_user_key = ndb.Key( 'User', user.user_id() )
        logged_user = logged_user_key.get()
        self.response.write( json.dumps( [ dict(user.to_dict(), **dict(id=user.key.id())) for user in  self.excludeCurrentUserFromUserList(User.query().fetch(), str(logged_user.key.id())) ] ) )
        return

    def excludeCurrentUserFromUserList(self, user_list, user_key):
        new_user_list = []
        for user in user_list:
            if str(user.key.id()) != user_key:
                new_user_list.append(user)
        return new_user_list
