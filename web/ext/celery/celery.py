# encoding: utf-8

from __future__ import absolute_import

try:
    import celery
except ImportError:
    print("Unable to find the celery package. To correct this, run: pip install celery")
    raise

from marrow.util.bunch import Bunch


class CeleryExtension(object):
    """Celery background task queue extension.
    
    See http://docs.celeryproject.org/en/latest/reference/celery.html#celery.Celery for valid
    initial configuration values (excluding 'main'), and the speical key 'settings' is provided
    as a celery configuration object and may either be a dot-notation module path or a dictionary.
    
    Especially important are the following configuration directives:
    
    * broker - communications broker
    * backend - permenant storage back-end
    * inlcude - a list of dot-notation package paths for organized child tasks
    """
    
    provides = ['celery']
    
    def __init__(self, **config):
        settings = config.pop('settings', None)
        
        if isinstance(settings, dict):
            settings = Bunch(settings)
        
        self.settings = settings
        self.config = Bunch(config)
    
    def start(self, context):
        context.celery = celery.Celery(
                __name__,
                **self.config
            )
        
        if self.settings:
            context.celery.config_from_object(self.settings)
