import webapp2
import jinja2
import os
import datetime

from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.api import images

from user import User
from post import Post
from blob_collection import BlobCollection

from view_all_comment import ViewAllCommentsOnAPostPage
from redirect_to_timeline import RedirectToTimelinePage
from user_profile import LoggedUserProfilePage
from user_profile_edit import LoggedUserProfileEditPage
from create_post import CreatePost
from upload_handler import UploadHandler
from selected_user_profile import SelectedUserProfilePage
from search_user import SearchPage
from api_request import APIServices
from update_follow import UpdateFollowStatus
from view_list import ViewFollowingFollowersList
from comment_on_post import AddCommentToPost

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

        collection_key = ndb.Key( 'BlobCollection', 1 )
        collection = collection_key.get()

        if collection == None:
            collection = BlobCollection( id = 1)
            collection.put()

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

        posts = self.getTimelinePost(logged_user, collection, images, 50)

        if len(posts) <= 0:
            message = "You currently do not have any post. Create one ..."
            query_string = "?failed=" + message
            url = "create-post" + query_string
            self.redirect( url )
            return

        template_values = {
            "url": url,
            "logged_user": logged_user,
            "user": user,
            "firstname": firstname,
            "lastname": lastname,
            "username": username,
            "profile_image": self.getProfileImage( logged_user.profile_image, collection, images ),
            "posts": posts,
            "sortPosts": self.sortPosts
        }

        template = JINJA_ENVIRONMENT.get_template( 'pages/index.html' )
        self.response.write( template.render( template_values ) )
        return

    def getProfileImage( self, image_name, collection, images ):
        try:
            index = collection.filenames.index(image_name)
            blob_key = collection.blobs[index]
            return images.get_serving_url(blob_key, secure_url=False)
        except:
            return "https://image.flaticon.com/icons/png/512/23/23228.png"

    def getTimelinePost( self, logged_user, collection, images, limit):
        posts = self.gettLoggedUserTimeline(logged_user)
        posts = self.sortPosts(posts)
        post_list = []
        if len(posts) <= limit:
            limit = len(posts)
        for post in posts:
            try:
                index = collection.filenames.index(post.image_label)
                blob_key = collection.blobs[index]
                images_url = images.get_serving_url(blob_key, secure_url=False)
            except:
                images_url = "https://4.bp.blogspot.com/-MowVHfLkoZU/VhgIRyPbIoI/AAAAAAAATtE/qHST4Q2YCCc/s1600/placeholder-image.jpg"
            created_by = self.getSelectedUser(post.created_by, collection, images)
            temp = {}
            temp["post"] = post
            temp["image_url"] = images_url
            temp["created_by"] = created_by
            post_list.append(temp)
        return post_list

    def gettLoggedUserTimeline(self, logged_user):
        post_list = []
        for user_id in logged_user.following:
            for user_intance in User.query().fetch():
                if str(user_intance.key.id()) == user_id:
                    user = ndb.Key( 'User', user_intance.key.id() ).get()
                    post_list.extend(self.getLoggedUserPostList(user.posts))
        post_list.extend(self.getLoggedUserPostList(logged_user.posts))
        return post_list

    def getLoggedUserPostList(self, posts):
        post_list = []
        if len(posts)<= 0:
            return post_list
        else:
            for post_id in posts:
                post = ndb.Key( 'Post', int(post_id) ).get()
                post_list.append(post)
        return post_list

    def sortPosts(self, posts):
        for i in range(1, len(posts)):
            j = i-1
            nxt_element = posts[i]
            try:
                while (posts[j].created_at < nxt_element.created_at) and (j >= 0):
                    posts[j+1] = posts[j]
                    j=j-1
                posts[j+1] = nxt_element
            except:
                pass
        return posts

    def getSelectedUser(self, user_key, collection, images):
        user = {}
        for user_in_datastore in User.query().fetch():
            if user_key == str(user_in_datastore.key.id()):
                user["user"] = user_in_datastore
                user["profile_image"] = self.getProfileImage( user_in_datastore.profile_image, collection, images )
        return user

app = webapp2.WSGIApplication(
    [
        webapp2.Route( r'/post/<post_key:[^/]+>/view-all-comments', handler=ViewAllCommentsOnAPostPage, name='view-all-comments'),
        webapp2.Route( r'/post/<post_key:[^/]+>/add-comment', handler=AddCommentToPost, name='add-comment-tro-post'),
        webapp2.Route( r'/view-list/<user_key:[^/]+>/<following_followers:[^/]+>', handler=ViewFollowingFollowersList, name='view-follow-list'),
        webapp2.Route( r'/<user_key:[^/]+>/update-follow-status', handler=UpdateFollowStatus, name='update-follow-status'),
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
