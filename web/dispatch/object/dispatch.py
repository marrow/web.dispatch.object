# encoding: utf-8

from __future__ import unicode_literals

from inspect import isclass, isroutine

from .util import nodefault, ipeek, str

if __debug__:
	import warnings
	from collections import deque


log = __import__('logging').getLogger(__name__)



class ObjectDispatch(object):
	__slots__ = ['protect']
	
	def __init__(self, protect=True):
		self.protect = protect
		
		if __debug__:
			log.debug("Object dispatcher prepared.", extra=dict(dispatcher=repr(self)))
		
		super(ObjectDispatch, self).__init__()
	
	def __repr__(self):
		return "ObjectDispatch(0x{id}, protect={self.protect!r})".format(id=id(self), self=self)
	
	def __call__(self, context, obj, path):
		dispatcher = repr(self)
		
		if __debug__:
			if not isinstance(path, deque):
				warnings.warn(
						"Your code is providing the path as a string; this will be cast to a deque in development but"
						"will explode gloriously if run in a production environment.",
						RuntimeWarning, stacklevel=1
					)
				
				if isinstance(path, str):
					path = deque(path.split('/')[1 if not path or path.startswith('/') else 0:])
				else:
					path = deque(path)
			
			log.debug("Preparing object dispatch.", extra=dict(
					dispatcher = dispatcher,
					context = repr(context),
					obj = repr(obj),
					path = list(path)
				))
		
		previous = None
		current = None
		protect = self.protect
		
		for previous, current in ipeek(path):  # Things can get hairy, so we need to track both this and the previous.
			if isclass(obj):  # We instantate classes we encounter during dispatch.
				obj = obj() if context is None else obj(context)
				if __debug__:
					log.debug("Instantiated class during descent.", extra=dict(
							dispatcher = dispatcher,
							instance = repr(obj),
						))
			
			if isroutine(obj):
				if __debug__:
					log.debug("Cowardly refusing to descend into a callable routine.", extra=dict(
							dispatcher = dispatcher,
							handler = obj,
						))
				break
			
			if protect and current.startswith('_'):  # We disallow private attribute access.
				if __debug__:
					log.debug("Attempt made to descend into protected attribute: " + current, extra=dict(
							dispatcher = dispatcher,
							current = current,
						))
				break  # Not being popped, this value will remain in the path.
			
			new = getattr(obj, current, nodefault)  # Attempt to get this attribute. Triggers __getattr__.
			
			if new is nodefault:  # We failed to find this attribute.
				break  # The current part, like with protected attributes, will be preserved in the path.
			
			if __debug__:
					log.debug("Retrieved attribute: " + current, extra=dict(
							dispatcher = dispatcher,
							source = obj,
							current = current,
							value = repr(new),
						))
				
			yield previous, obj, False  # Commit the previously walked step.
			
			obj = new  # Continue processing the next level of path from this point.
		
		else:  # No path left to consume. Wherever we go, there we are. This handles the "empty path" case.
			obj = (obj() if context is None else obj(context)) if isclass(obj) else obj
			
			if __debug__:
				log.debug("Dispatch complete due to exhausted path.", extra=dict(
						dispatcher = dispatcher,
						handler = repr(obj),
					))
			
			yield current, obj, True
			return
		
		# We bailed, so "obj" represents the last found attribute, "previous" is the path element matching that
		# object, and "current" represents the failed element. Because we bailed, "current" remains in the path.
		
		if __debug__:
			log.debug("Dispatch interrupted attempting to resolve attribute: " + current, extra=dict(
					dispatcher = dispatcher,
					handler = repr(obj),
					endpoint = callable(obj),
					previous = previous,
					attribute = current,
				))
		
		yield previous, obj, callable(obj)
