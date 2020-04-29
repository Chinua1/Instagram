import webapp2

class RedirectToTimelinePage( webapp2.RequestHandler ):
    def get( self ):
        self.redirect("/timeline")
        return
