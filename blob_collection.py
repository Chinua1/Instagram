from google.appengine.ext import ndb

class BlobCollection( ndb.Model ):
    filenames = ndb.StringProperty( repeated = True )
    blobs = ndb.BlobKeyProperty( repeated = True )
