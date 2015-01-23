# encoding: utf-8

from marrow.mailer import Mailer


class MailExtension(object):
    provides = ['mail']
    
    def __init__(self, **config):
        """Executed to configure the extension."""
        super(MailExtension, self).__init__()
        
        context.mailer = Mailer(config)
    
    def start(self, context):
        """Executed during application startup just after binding the server."""
        context.mailer.start()
    
    def stop(self, context):
        """Executed during application shutdown after the last request has been served."""
        context.mailer.stop()
