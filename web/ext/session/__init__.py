# encoding: utf-8



class BeakerSessionProvider(object):
    uses = []
    needs = []
    
    def __init__(self, config=None):
        """Called during startup."""
        
        config = config or dict()
        
        self.options = dict(
                invalidate_corrupt=True,
                type=None, 
                data_dir=None,
                key='beaker.session.id', 
                timeout=None,
                secret=None,
                log_file=None
            )
        
        self.options.update(dict(config))
        
        pass
    
    def stop(self):
        """Called during shutdown."""
        pass
    
    def __call__(self, context):
        """Called during preparation."""
        pass




class SessionExtension(object):
    uses = ['database']
    provides = ['session']
    
    defaults = dict(
            
        )
    
    def __init__(self, config):
        """Executed to configure the extension."""
        super(SessionExtension, self).__init__()
        
        # TODO: Look this up w/ sane (tempfile) default.
        self.Provider = BeakerSessionProvider
        self.config = config
        
        self.uses.extend(getattr(self.Provider, 'uses', [])
        self.needs.extend(getattr(self.Provider, 'needs', [])
    
    def start(self):
        """Executed during application startup just after binding the server."""
        self.provider = self.Provider(self.config)
    
    def stop(self):
        """Executed during application shutdown after the last request has been served."""
        self.provider.stop()
        self.provider = None
    
    def prepare(self, context):
        """Executed during request set-up."""
        context.session = self.provider(context)
    
    def after(self, context, exc=None):
        """Executed after dispatch has returned and the response populated, prior to anything being sent to the client."""
        if self.auto and not exc:
            context.session.save()
