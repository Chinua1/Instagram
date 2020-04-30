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

class LoggedUserProfilePage( webapp2.RequestHandler ):
    def get( self ):
        url = ''
        logged_user = None
        user = users.get_current_user()
        firstname = ''
        lastname = ''
        username = ''
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

        posts = self.getLoggedUserPosts( self.sortPosts(logged_user.posts), collection, images )

        template_values = {
            "url": url,
            "logged_user": logged_user,
            "user": user,
            "profile_image_url": self.getProfileImage( logged_user.profile_image, collection, images ),
            "post_owner_key": None,
            "firstname": firstname,
            "lastname": lastname,
            "username": username,
            "fullname": self.getFullName(lastname, firstname),
            "posts": posts,
            "post_count": len(logged_user.posts),
            "followers": len(logged_user.following),
            "following": len(logged_user.followers),

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
            index = collection.filenames.index(post.image_label)
            blob_key = collection.blobs[index]
            images_url = images.get_serving_url(blob_key, secure_url=False)
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

    def sortPosts(self, posts):
        for i in range(1, len(posts)):
            j = i-1
            nxt_element = posts[i]
            while (posts[j].created_at < nxt_element.created_at) and (j >= 0):
                posts[j+1] = posts[j]
                j=j-1
            posts[j+1] = nxt_element
        return posts
