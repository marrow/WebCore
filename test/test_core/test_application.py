# encoding: utf-8

from __future__ import unicode_literals

from unittest import TestCase
from inspect import isclass

from web.core.application import Application


class TestApplicationParts(TestCase):
	def setUp(self):
		self.app = Application("Hi.")
	
	def test_application_attributes(self):
		assert isclass(self.app.RequestContext), "Non-class prepared request context."

