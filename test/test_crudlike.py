# encoding: utf-8

from __future__ import unicode_literals

from collections import deque
from web.dispatch.object import ObjectDispatch

from crudlike import Person, People, Root


dispatch = ObjectDispatch()


class TestCrudlikeRoot(object):
	def test_resolve_root(self):
		result = list(dispatch(None, Root, ''))
		assert len(result) == 1
		assert result[0].endpoint  # Explicit endpoint reached.
		assert isinstance(result[0].handler, Root)  # Intermediate is Root instance.
	
	def test_no_resolve_other(self):
		result = list(dispatch(None, Root, '/foo'))
		assert len(result) == 1
		assert not result[0].endpoint  # Endpoint not reached.
		assert isinstance(result[0].handler, Root)  # Intermediate is Root instance.


class TestCrudlikeCollection(object):
	def test_resolve_user_collection(self):
		result = list(dispatch(None, Root, deque(['user'])))
		assert len(result) == 2
		assert result[1].endpoint == True  # Endpoint reached.
		assert isinstance(result[0].handler, Root)  # Intermediate is Root instance.
		assert isinstance(result[1].handler, People)  # Endpoint is People instance.
		assert result[1].handler() == "I'm all people."
	
	def test_resolve_specific_user(self):
		result = list(dispatch(None, Root, deque(['user', 'GothAlice'])))
		assert len(result) == 3
		assert result[2].endpoint == True  # Endpoint reached.
		assert isinstance(result[0].handler, Root)  # Intermediate is Root instance.
		assert isinstance(result[1].handler, People)  # Intermediate is People instance.
		assert isinstance(result[2].handler, Person)  # Endpoint is Person instance.
		assert result[2].handler() == "Hi, I'm GothAlice"
	
	def test_resolve_specific_user_action(self):
		result = list(dispatch(None, Root, deque(['user', 'GothAlice', 'foo'])))
		assert len(result) == 4
		assert result[3].endpoint == True  # Endpoint reached.
		assert isinstance(result[0].handler, Root)  # Intermediate is Root instance.
		assert isinstance(result[1].handler, People)  # Intermediate is People instance.
		assert isinstance(result[2].handler, Person)  # Endpoint is Person instance.
		assert result[3].handler() == "I'm also GothAlice"
