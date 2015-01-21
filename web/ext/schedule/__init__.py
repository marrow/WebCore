# encoding: utf-8

from __future__ import unicode_literals

from marrow.package.loader import traverse, load

try:
	import apscheduler
	from apscheduler.schedulers.background import BackgroundScheduler
except ImportError:
	raise ImportError('You need to install apscheduler to use this extension.')


class APSchedulerExtension(object):
	__slots__ = ('scheduler', )
	provides = ['scheduler']
	
	def __init__(self, scheduler=BackgroundScheduler, **config):
		super(APSchedulerExtension, self).__init__()
		
		self.scheduler = load(scheduler)(**config)
	
	def start(self, context):
		scheduler = context.scheduler = self.scheduler
		scheduler.start()
	
	def stop(self, context):
		context.scheduler.shutdown()
