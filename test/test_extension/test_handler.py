import pytest
from webob import Request
from webob.exc import HTTPNotFound

from web.core import Application
from web.core.testing import MockRequest
from web.core.ext.handler import StatusHandlers


def mock_endpoint(context, status, state=None):
	context.response.status_int = int(status)
	mock_endpoint.state = state
	return state


@pytest.fixture
def app():
	return Application(mock_endpoint, [StatusHandlers({
			HTTPNotFound: '/404/notfound',
			503: '/503/maintenance',
		})])


def test_notfound(app):
	with MockRequest('/404') as request:
		response = request.send(app)
	
	assert response.text == 'notfound'
	assert response.status_int == 404
	assert mock_endpoint.state == 'notfound'


def test_maintenance(app):
	with MockRequest('/404') as request:
		response = request.send(app)
	
	assert response.text == 'notfound'
	assert response.status_int == 404
	assert mock_endpoint.state == 'notfound'

