# encoding: utf-8


class Person(object):
	def __init__(self, username):
		self._username = username
	
	def __call__(self):
		return "Hi, I'm " + self._username
	
	def foo(self):
		return "I'm also " + self._username


class People(object):
	def __init__(self, context=None):
		self._ctx = context
	
	def __call__(self):
		return "I'm all people."
	
	def __getattr__(self, username, **kw):
		return Person(username)


class Root(object):
	def __init__(self, context=None):
		self._ctx = context
	
	user = People
