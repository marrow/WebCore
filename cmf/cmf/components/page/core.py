# encoding: utf-8

"""

Page controller core JSON API methods.

"""

from datetime               import datetime
from tg                     import expose, url, TGController


log = __import__('logging').getLogger(__name__)
__all__ = ['CoreMethods']


class CoreMethods(TGController):
    def __init__(self, controller):
        self.controller = controller
        super(CoreMethods, self).__init__()
    
    @expose()
    def index(self):
        return "it works"
    
    @expose('json')
    def getContent(self, tg_format="application/json"):
        # TODO: Security check.  Ensure the user attempting to set the property has the rights to do so.
        
        try:
            return dict(
                    status="ok",
                    message="Successfully retrieved page content.",
                    content=self.controller.renderer.render(self.controller, self.controller.asset)
                )
            
        except:
            log.exception("Error rendering content.")
        
        return dict(status="error", message="Unable to retrieve page content.")
