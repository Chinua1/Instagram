import webapp2
import jinja2
import os
import datetime
import json
import time

from google.appengine.api import users
from google.appengine.ext import ndb
from user import User

class UpdateFollowStatus( webapp2.RequestHandler ):
    def post( self, user_key ):
        self.response.headers[ 'Content-Type' ] = 'text/html'
        user = users.get_current_user()
        logged_user_key = ndb.Key( 'User', user.user_id() )
        logged_user = logged_user_key.get()
        selected_user = self.getSelectedUser(user_key)

        if self.getFollowShipStatus(logged_user.following, str(selected_user.key.id())):
            logged_user.following.remove(user_key)
            logged_user.put()

            selected_user.followers.remove(str(logged_user.key.id()))
            selected_user.put()
        else:
            logged_user.following.append(user_key)
            logged_user.put()

            selected_user.followers.append(str(logged_user.key.id()))
            selected_user.put()

        self.redirect('/' + user_key + '/profile')
        return

    def excludeCurrentUserFromUserList(self, user_list, user_key):
        new_user_list = []
        for user in user_list:
            if str(user.key.id()) != user_key:
                new_user_list.append(user)
        return new_user_list

    def getSelectedUser(self, user_key):
        user = None
        for user_in_datastore in User.query().fetch():
            if user_key == str(user_in_datastore.key.id()):
                user = user_in_datastore
        return user

    def getFollowShipStatus( self, following, logged_user_key):
        is_followed = False
        for key in following:
            if key == logged_user_key:
                is_followed = True
        return is_followed
