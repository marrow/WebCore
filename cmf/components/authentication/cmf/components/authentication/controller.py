# encoding: utf-8

"""

Base asset controller.

"""

import                      md5

from sqlalchemy             import or_, orm
from datetime               import datetime
from tg                     import request, session, expose, flash, redirect, url
from pylons.i18n            import ugettext as _

from cmf.core               import view, action, View, AuthenticatedAction, AnonymousAction
from cmf.util               import AttrDict

from cmf.components.asset.controller import AssetController
from cmf.components.account.model import Account


log = __import__('logging').getLogger(__name__)
__all__ = ['AuthenticationController']


class AuthenticationController(AssetController):
    """TODO: Docstring incomplete."""
    
    #TODO: Deprecated.
    authenticate    = AnonymousAction("Sign In", "Enter your credentials to gain additional access to the site.", 'base-auth-signin')
    leave           = AuthenticatedAction("Sign Out", "Remove your credentials from the session.", 'base-auth-signout')
    
    @expose()
    def _view_default(self):
        redirect('/')
    
    @expose('genshi:cmf.components.authentication.views.authenticate')
    @action(AnonymousAction, "Enter your credentials to gain additional access to the site.", icon='base-auth-signin')
    def _action_authenticate(self, action='view', **kw):
        log.debug("%r %r", action, kw)
        
        target = AttrDict()
        target.url = session.get('cmf.authentication.target', request.referrer if request.referrer else '/')
        target.asset = session.get('cmf.authentication.target.asset', None)
        
        session['cmf.authentication.target'] = target.url
        
        if action == 'submit':
            data = AttrDict(kw)
            
            try:
                account = Account.query.filter_by(_password=md5.md5(data.password).hexdigest()).filter(or_(Account.name == data.account, Account.email == data.account)).one()
                
                session['cmf.authentication.account'] = account
                session.save()
                
                flash("Welcome back, %s." % (account.title, ), 'success')
                redirect(data.target)
                return dict()
            
            except orm.exc.NoResultFound:
                flash("Unable to authenticate with these credentials.", 'error')
        
        # if 'cmf.authentication.target' in session: del session['cmf.authentication.target']
        # if 'cmf.authentication.target.asset' in session: del session['cmf.authentication.target.asset']
        
        return dict(target=target)
    
    @expose()
    @action(AuthenticatedAction, "Sign Out", "Remove your credentials from the session.", icon='base-auth-signout')
    def _action_leave(self):
        if 'cmf.authentication.account' in session:
            flash("Goodbye, %s." % (session['cmf.authentication.account'].title), 'success')
            del session['cmf.authentication.account']
            session.save()
        
        redirect(request.referrer if request.referrer else '/')
