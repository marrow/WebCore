from web.core.application import Application
from web.ext.debug import DebugExtension

def serve(root):
	Application(root, extensions=[DebugExtension()]).serve('waitress')
