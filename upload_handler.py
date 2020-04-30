import webapp2
import jinja2
import os

import time
from datetime import datetime

from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers

from user import User
from post import Post

class UploadHandler( blobstore_handlers.BlobstoreUploadHandler ):
    def post( self ):
        action = self.request.get('button')
        user = users.get_current_user()
        logged_user_key = ndb.Key( 'User', user.user_id() )
        logged_user = logged_user_key.get()
        uploads = None

        if action == "Post":
            if len(self.get_uploads()) >= 1:
                uploads = self.get_uploads()[ 0 ]
                blobinfo = blobstore.BlobInfo( uploads.key() )
                extension = blobinfo.filename.split(".")[1]
                if str(extension).lower() == "jpg" or str(extension).lower() == "png":
                    post_image_name = "instagram" + str(time.mktime(datetime.now().timetuple())) + "." + extension
                    post_caption = self.request.get( 'post_caption' )

                    if post_caption != "":
                        collection_key = ndb.Key( 'BlobCollection', 1 )
                        collection = collection_key.get()
                        collection.filenames.append( post_image_name )
                        collection.blobs.append( uploads.key() )
                        collection.put()

                        new_post = Post(
                            image_label = post_image_name,
                            post_caption = post_caption,
                            created_at = datetime.now()
                        )

                        logged_user.posts.append(new_post)
                        logged_user.put()
                        url = "/timeline"
                        self.redirect(url)
                        return
                    else:
                        message = "Invalid input. Please add a caption."
                        query_string = "?failed=" + message
                        url = "/create-post" + query_string
                        self.redirect(url)
                        return
                else:
                    message = "Invalid file type. Only JPG or PNG are permitted file type"
                    query_string = "?failed=" + message
                    url = "/create-post" + query_string
                    self.redirect(url)
                    return
            else:
                message = "No image selected. Please select an image file."
                query_string = "?failed=" + message
                url = "/create-post" + query_string
                self.redirect(url)
                return
