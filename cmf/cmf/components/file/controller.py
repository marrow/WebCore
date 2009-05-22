# encoding: utf-8

"""

Base asset controller.

"""

import                      pkg_resources, StringIO

from tg                     import request, response, session, expose, flash, redirect, url, validate
from pylons.i18n            import ugettext as _
from datetime               import datetime

from tw.api                 import WidgetsList
from tw.forms               import Form, ListForm, TextField, CalendarDatePicker, SingleSelectField, TextArea, FileField
from formencode.validators  import Int, NotEmpty, DateConverter, DateValidator

from cmf.core               import view, action, View, OwnerAction

from cmf.components.asset.controller import AssetController


log = __import__('logging').getLogger(__name__)
__all__ = ['FileController']



class SerialForm(Form):
    template = "genshi:cmf.components.asset.widgets.form"


class FileController(AssetController):
    """TODO: Docstring incomplete."""
    
    # TODO: Deprecated.
    preview         = View("Preview", "View the file with details.", 'base-file')
    modify          = OwnerAction("Modify", "Modify the file contents.", 'base-page-modify')
    
    # @property
    # def renderer(self):
    #     return list(pkg_resources.iter_entry_points('turbocmf.page.renderer', self.asset.renderer))[0].load()(self.asset)
    
    @expose('genshi:cmf.components.file.views.preview')
    @view(View, "Preview", "View the file with details.", icon='base-file')
    def _view_preview(self):
        return dict(content=StringIO.StringIO(self.asset.content))
    
    @expose('genshi:cmf.components.file.views.modify')
    @action(OwnerAction, "Modify", "Modify the file contents.", icon='base-page-modify')
    def _action_modify(self, **kw):
        fields = [
                TextField("title", validator=NotEmpty, help_text="Enter the display title of this asset. This is displayed at the top of the document, in lists, and in searches."),
                TextArea("description", attrs=dict(rows=5, cols=25), help_text="The description is used in list views and searches, and appears at the top of the document in a distinct style."),
                FileField("content", help_text="Upload the content for this file instance.")
            ]
        
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
                        if name == 'content':
                            self.asset.content = value.file.read()
                            self.asset.mime = value.type
                            continue
                        
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
    
    @expose(content_type='CUSTOM/LEAVE')
    def _view_original(self, fake_name=None, *args, **kw):
        response.content_type = self.asset.mime
        response.headers['Content-Disposition'] = 'inline; filename="%s.mp4"' % (fake_name if fake_name else self.asset.name, )
        
        log.debug("name = %r, %r", fake_name, kw)
        
        result = StringIO.StringIO(self.asset.content)
        return result.getvalue()
    
    @expose(content_type='CUSTOM/LEAVE')
    def _view_download(self, fake_name=None):
        response.content_type = self.asset.mime
        response.headers['Content-Disposition'] = 'attachment; filename="%s"' % (fake_name if fake_name else self.asset.name, )
        
        result = StringIO.StringIO(self.asset.content)
        return result.getvalue()
    
