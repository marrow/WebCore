# encoding: utf-8

"""

Base asset controller.

"""

from tg                     import request, session, expose
from pylons.i18n            import ugettext as _

from cmf.core               import view, AuthenticatedView

from cmf.components.asset.controller import AssetController

from docutils.core              import publish_parts


log = __import__('logging').getLogger(__name__)
__all__ = ['Extension']



class Extension(AssetController):
    """TODO: Docstring incomplete."""
    
    about           = AuthenticatedView("About", "Display information about this extension.", 'extension-about')
    
    @expose('genshi:cmf.components.extension.views.about')
    @view(AuthenticatedView, "About", "Display information about this extension.", icon='extension-about')
    def _view_about(self):
        from cmf.core import components
        
        component = None
        
        for i in components.itervalues():
            if type(self) is i.controller:
                component = i
                break
        
        description = component.description
        
        if description:
            description = publish_parts(description, writer_name="html", settings_overrides=dict(initial_header_level=3))['html_body']
        
        return dict(extension=component, description=description)
        
        raise ValueError
