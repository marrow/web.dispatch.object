# encoding: utf-8

"""Objects used to evaluate dispatch in tests."""


def init(self, context):
	self._ctx = context


def path(path):
	return deque(path.split('/')[1:])


def function(context, *args):
	return 'function /' + '/'.join(args)


class Simple:
	_protected = True
	__init__ = init
	static = "foo"
	
	class foo:
		__init__ = init
		
		class bar:
			__init__ = init
			
			def baz(self):
				return "baz"


class CallableShallow:
	__init__ = init
	
	def __call__(self, *args):
		return '/' + '/'.join(args)


class CallableDeep:
	__init__ = init
	
	class foo:
		__init__ = init
		
		class bar:
			__init__ = init
			
			def __call__(self, method):
				return method


class CallableMixed:
	__init__ = init
	
	def __call__(self, *args):
		return '/' + '/'.join(args)
	
	class foo:
		__init__ = init
		
		class bar:
			__init__ = init
			
			def baz(self):
				return "baz"
