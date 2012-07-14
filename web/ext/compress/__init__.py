# encoding: utf-8


class CompressionExtension(object):
    provides = ['compression']
    
    def __init__(self, context):
        """Executed to configure the extension."""
        super(CompressionExtension, self).__init__()
