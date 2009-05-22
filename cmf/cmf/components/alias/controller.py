# encoding: utf-8

"""

Base asset controller.

"""

from tg                     import request, session, expose, flash, redirect, url
from pylons.i18n            import ugettext as _
from datetime               import datetime

from cmf.core               import View

from cmf.components.asset.controller import AssetController


log = __import__('logging').getLogger(__name__)
__all__ = ['AliasController']



class AliasController(AssetController):
    """TODO: Docstring incomplete."""
    
    default         = View("Redirect", "Redirect.", 'base-alias')
    modify          = OwnerAction("Modify", "Modify the alias target.", 'base-alias-modify')
    
    
    @expose()
    @view(View, "Redirect", "Redirect.", icon='base-alias')
    def _view_default(self):
        flash("The resource you requested is no longer available at the old URL.  Please update your bookmarks.", 'warning')
        redirect(self.asset.target)
    
    @expose('genshi:cmf.components.page.views.modify')
    @action(OwnerAction, "Modify", "Modify the page contents.", icon='base-page-modify')
    def _action_modify(self, **kw):
        fields = [
                TextField("title", validator=NotEmpty, help_text="Enter the display title of this asset. This is displayed at the top of the document, in lists, and in searches."),
                TextArea("description", attrs=dict(rows=5, cols=25), help_text="The description is used in list views and searches, and appears at the top of the document in a distinct style.")
            ]
        
        # TODO: Allow the renderer to define a editor field.
        fields.extend(self.renderer.editor)
        
        form = SerialForm("modify", submit_text="Save Changes", fields=fields)
        
        if kw:
            @validate(form=form)
            def get_errors(self, tg_errors=None, **data):
                return tg_errors, data
            
            errors, data = get_errors(self, **kw)
            
            if not errors:
                from cmf.components.asset.model import session
                
                self.asset.modified = datetime.now()
                
                try:
                    for name, value in data.iteritems():
                        setattr(self.asset, name, value)
                
                except:
                    log.exception("Error updating %r.", self.asset)
                    session.rollback()
                    flash("Error updating asset.", 'error')
                
                else:
                    session.commit()
                    flash("Successfully updated asset.", 'success')
                    redirect(self.asset.path)
        
        return dict(controller=self, asset=self.asset, form=form)
