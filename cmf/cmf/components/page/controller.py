# encoding: utf-8

"""

Base asset controller.

"""

import                      pkg_resources

from tg                     import request, session, expose, flash, redirect, url, validate
from pylons.i18n            import ugettext as _
from datetime               import datetime

from tw.api                 import WidgetsList
from tw.forms               import Form, ListForm, TextField, CalendarDatePicker, SingleSelectField, TextArea
from formencode.validators  import Int, NotEmpty, DateConverter, DateValidator

from cmf.core               import view, action, View, OwnerAction

from cmf.components.asset.controller    import AssetController
from cmf.components.page.core           import CoreMethods


log = __import__('logging').getLogger(__name__)
__all__ = ['PageController']



class SerialForm(Form):
    template = "genshi:cmf.components.asset.widgets.form"


class PageController(AssetController):
    """TODO: Docstring incomplete."""
    
    # TODO: Deprecated.
    render          = View("Normal", "View the page contents.", 'base-page')
    modify          = OwnerAction("Modify", "Modify the page contents.", 'base-page-modify')
    
    def __init__(self, *args, **kw):
        super(PageController, self).__init__(*args, **kw)
        self._api_page = CoreMethods(self)
    
    @property
    def renderer(self):
        return list(pkg_resources.iter_entry_points('turbocmf.page.renderer', self.asset.renderer))[0].load()(self.asset)
    
    @expose('genshi:cmf.components.page.views.render')
    @view(View, "Normal", "View the page contents.", icon='base-page')
    def _view_render(self):
        return dict(content=self.renderer.render(self, self.asset))
    
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
