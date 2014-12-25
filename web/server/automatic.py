# encoding: utf-8

"""A production quality flup-based FastCGI server."""

from __future__ import unicode_literals, print_function


def serve(application, host='127.0.0.1', port=8080):
	"""Automatically detect the server to use.
	
	Note that the options available are quite limited when using detection.
	"""
	raise NotImplementedError()
