# encoding: utf-8

try:
    import transaction
except ImportError:
    raise ImportError("Unable to import transaction; pip install transaction to fix this.")


class TransactionExtension(object):
    uses = []
    needs = []
    provides = ['transaction']

    def __init__(self, config):
        """Executed to configure the extension."""
        super(TransactionExtension, self).__init__()

    def start(self):
        """Executed during application startup just after binding the server."""
        pass

    def stop(self):
        """Executed during application shutdown after the last request has been served."""
        pass

    def prepare(self, context):
        """Executed during request set-up."""
        pass

    def after(self, context, exc=None):
        """Executed after dispatch has returned and the response populated, prior to anything being sent to the client."""
        pass
