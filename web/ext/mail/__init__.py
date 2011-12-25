# encoding: utf-8

from marrow.mailer import Mailer


class MailExtension(object):
    uses = []
    needs = []
    provides = ['mail']
    
    def __init__(self, config):
        """Executed to configure the extension."""
        super(MailExtension, self).__init__()
        
        self.mailer = Mailer(config)
    
    def start(self):
        """Executed during application startup just after binding the server."""
        self.mailer.start()
    
    def stop(self):
        """Executed during application shutdown after the last request has been served."""
        self.mailer.stop()
    
    def prepare(self, context):
        """Executed during request set-up."""
        context.mail = self.mailer
    
    def after(self, context, exc=None):
        """Executed after dispatch has returned and the response populated, prior to anything being sent to the client."""
        pass # conditional sending
