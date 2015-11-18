# encoding: utf-8

from inspect import isclass, isroutine

from webob.exc import HTTPNotFound
from marrow.package.loader import load


log = __import__('logging').getLogger(__name__)

nodefault = object()  # Sentinel value.


def ipeek(d):
	"""Iterate through a deque, popping elements from the left after they have been seen."""
	last = None
	
	# We eat trailing slashes.  No sir, can't say we like 'em.
	while d and d[-1] == '':
		d.pop()
	
	while d:
		yield last, d[0]
		last = d.popleft()


class ObjectDispatch(object):
	__slots__ = ['protect']
	
	def __init__(self, protect=True):
		self.protect = protect
		
		super(ObjectDispatch, self).__init__()
	
	def __call__(self, context, obj, path):
		previous = None
		current = None
		protect = self.protect
		
		for previous, current in ipeek(path):  # Things can get hairy, so we need to track both this and the previous.
			if isclass(obj):  # We instantate classes we encounter during dispatch.
				obj = obj(context)
			
			if protect and current.startswith('_'):  # We disallow private attribute access.
				break  # Not being popped, this value will remain in the path.
			
			new = getattr(obj, current, nodefault)  # Attempt to get this attribute. Triggers __getattr__.
			
			if new is nodefault:  # We failed to find this attribute.
				break  # The current part, like with protected attributes, will be preserved in the path.
			
			yield previous, obj, False  # Commit the previously walked step.
			
			obj = new  # Continue processing the next level of path from this point.
		
		else:  # No path left to consume. Wherever we go, there we are. This handles the "empty path" case.
			yield current, obj(context) if isclass(obj) else obj, True
			return
		
		# We bailed, so "obj" represents the last found attribute, "previous" is the path element matching that object,
		# and "current" represents the failed element. Because we bailed, "current" remains in the path.
		yield previous, obj, callable(obj)
