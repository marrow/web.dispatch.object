# encoding: utf-8

from inspect import isclass, isroutine

from webob.exc import HTTPNotFound
from marrow.package.loader import load


log = __import__('logging').getLogger(__name__)


def ipeek(d):
	"""Iterate through a list, popping elements after they have been seen."""
	while d:
		yield d[0]
		d.pop(0)


class ObjectDispatch(object):
	def __init__(self, config):
		self.trailing = config.get('slashes', True)
		super(ObjectDispatch, self).__init__()
	
	def __call__(self, context, root):
		if __debug__:
			log.debug("Starting object dispatch.", extra=dict(
					request = id(context.request),
					script_name = context.request.script_name,
					path_info = context.request.path_info,
					root = repr(root)
				))
		
		path = context.request.path_info.split('/')
		trailing = False
		
		# Capture and eliminate the final, empty path element.
		# If present there was a trailing slash in the original path.
		if path[-1:] == ['']:
			trailing = True
			path.pop()
		
		# We don't care about leading slashes.
		if path[:1] == ['']:
			path.pop(0)
		
		if __debug__:
			log.debug("Search path identified.", extra=dict(request=id(context.request), path=path))
		
		last = ''
		parent = None
		current = root
		
		# Iterate through and consume the path element (chunk) list.
		for chunk in ipeek(path):
			if __debug__:
				log.debug("Begin dispatch step.", extra=dict(request=id(context.request),
						chunk = chunk,
						path = path,
						current = repr(current)
					))
				
			if isclass(current):
				if __debug__:
					log.debug("Instantiating class.", extra=dict(request=id(context.request)))
				current = current(context)
			
			parent = current
			
			# Security: prevent access to real private attributes.
			# This is tricky as we need to avoid __getattr__ behaviour.
			if chunk[0] == '_' and (hasattr(current.__class__, chunk) or chunk in current.__dict__):
				log.warn("Blocked access to private attribute.", extra=dict(request=id(context.request)))
				raise HTTPNotFound()
			
			current = getattr(parent, str(chunk), None)
			if __debug__ and current:
				log.debug("Found attribute.", extra=dict(request=id(context.request), current=repr(current)))
			
			# If there is no attribute (real or via __getattr__) try the __lookup__ method to re-route.
			if not current:
				if not callable(parent):
					try:
						fallback = parent.__lookup__
					except AttributeError:
						raise HTTPNotFound()
					else:
						current, consumed = fallback(*path)
						chunk = '/'.join(consumed)
						del path[:len(consumed)]
				else:
					if isroutine(parent):
						yield last.split('/'), parent, True
					else:
						yield last.split('/'), parent, True
					return
			
			yield last.split('/'), parent, False
			
			last = str(chunk)
		
		if isclass(current):
			current = current(context)
		
		yield last.split('/'), current, True


if __debug__ and __name__ == '__main__':  # pragma: no cover
	from marrow.util.bunch import Bunch
	from marrow.logging import Log, DEBUG
	
	request = Bunch(remainder='/')
	context = Bunch(log=Log(level=DEBUG).name(__file__), request=request)
	
	class Controller(object):
		def __init__(self, context):
			self._ctx = context
	
	class RootController(Controller):
		def __call__(self):
			return "Hello world!"
	
	router = ObjectDispatch(dict())
	
	for i,j,k in router(context, RootController):
		context.log.info(path=i,obj=j,final=k)
	
	request.remainder = '/about/staff'

	class AboutController(Controller):
		def staff(self):
			return "Staff page."
	
	class RootController(Controller):
		about = AboutController
	
	print()
	for i,j,k in router(context, RootController):
		context.log.info(path=i,obj=j,final=k)
	
	def index(context):
		return "Foo!"
	
	print()
	for i,j,k in router(context, index):
		context.log.info(path=i,obj=j,final=k)
