import webapp2
import jinja2
import os
import datetime

from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.ext import blobstore
from google.appengine.api import images


from user import User

start = os.path.dirname( __file__ )
rel_path = os.path.join(start, 'templates')
abs_path = os.path.realpath(rel_path)

JINJA_ENVIRONMENT = jinja2.Environment(
    loader = jinja2.FileSystemLoader( abs_path ),
    extensions = [ 'jinja2.ext.autoescape' ],
    autoescape = True
)

class SelectedUserProfilePage( webapp2.RequestHandler ):
    def get( self, user_key ):
        url = ''
        selected_user = self.getSelectedUser(user_key)
        user = users.get_current_user()
        collection_key = ndb.Key( 'BlobCollection', 1 )
        collection = collection_key.get()

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
                    pass
                else:
                    temp_url = "/edit-profile"
                    self.redirect(temp_url)
                    return
        else:
            url = users.create_login_url( self.request.uri )
            self.redirect( url )
            return

        posts = reversed(self.getLoggedUserPosts( self.sortPosts(selected_user.posts), collection, images ))

        template_values = {
            "url": url,
            "logged_user": logged_user,
            "selected_user": selected_user,
            "profile_image_url": self.getProfileImage( selected_user.profile_image, collection, images ),
            "post_owner_key": user_key,
            "user": user,
            "firstname": str(selected_user.firstname).capitalize(),
            "lastname": str(selected_user.lastname).capitalize(),
            "username": str(selected_user.username).lower(),
            "fullname": str(self.getFullName(selected_user.lastname, selected_user.firstname)).capitalize(),
            "posts": posts,
            "post_count": len(selected_user.posts),
            "followers": len(selected_user.followers),
            "following": len(selected_user.following),
            "is_followed": self.getFollowShipStatus(logged_user.following, user_key),
            "following_followers_id": selected_user.key.id()
        }
        template = JINJA_ENVIRONMENT.get_template( 'pages/profile.html' )
        self.response.write( template.render( template_values ) )
        return

    def getProfileImage( self, image_name, collection, images ):
        try:
            index = collection.filenames.index(image_name)
            blob_key = collection.blobs[index]
            return images.get_serving_url(blob_key, secure_url=False)
        except:
            return "https://image.flaticon.com/icons/png/512/23/23228.png"

    def getLoggedUserPosts( self, posts, collection, images ):
        generated_posts = []
        posts = self.getAllPostForLoggedUser(posts)
        for post in posts:
            try:
                index = collection.filenames.index(post.image_label)
                blob_key = collection.blobs[index]
                images_url = images.get_serving_url(blob_key, secure_url=False)
            except:
                images_url = "https://4.bp.blogspot.com/-MowVHfLkoZU/VhgIRyPbIoI/AAAAAAAATtE/qHST4Q2YCCc/s1600/placeholder-image.jpg"
            temp = {}
            temp["post"] = post
            temp["image_url"] = images_url
            generated_posts.append(temp)

        return generated_posts

    def getAllPostForLoggedUser(self, posts):
        post_list = []
        if len(posts)<= 0:
            return posts
        else:
            for post_id in posts:
                post = ndb.Key( 'Post', int(post_id) ).get()
                post_list.append(post)
        return post_list

    def getFullName( self, firstname, lastname):
        return lastname + " " + firstname

    def getFollowShipStatus( self, following, logged_user_key):
        is_followed = False
        for key in following:
            if key == logged_user_key:
                is_followed = True
        return is_followed

    def getSelectedUser(self, user_key):
        user = None
        for user_in_datastore in User.query().fetch():
            if user_key == str(user_in_datastore.key.id()):
                user = user_in_datastore

        return user

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
