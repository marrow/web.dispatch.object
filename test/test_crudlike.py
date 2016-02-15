# encoding: utf-8

from __future__ import unicode_literals

from collections import deque
from web.dispatch.object import ObjectDispatch

from crudlike import Person, People, Root


dispatch = ObjectDispatch()


class TestCrudlikeRoot(object):
	def test_resolve_root(self):
		result = list(dispatch(None, Root, deque([])))
		assert len(result) == 1
		assert result[0][2] == True  # Explicit endpoint reached.
		assert isinstance(result[0][1], Root)  # Intermediate is Root instance.
	
	def test_no_resolve_other(self):
		result = list(dispatch(None, Root, deque(['foo'])))
		assert len(result) == 1
		assert result[0][2] == False  # Endpoint not reached.
		assert isinstance(result[0][1], Root)  # Intermediate is Root instance.


class TestCrudlikeCollection(object):
	def test_resolve_user_collection(self):
		result = list(dispatch(None, Root, deque(['user'])))
		assert len(result) == 2
		assert result[1][2] == True  # Endpoint reached.
		assert isinstance(result[0][1], Root)  # Intermediate is Root instance.
		assert isinstance(result[1][1], People)  # Endpoint is People instance.
		assert result[1][1]() == "I'm all people."
	
	def test_resolve_specific_user(self):
		result = list(dispatch(None, Root, deque(['user', 'GothAlice'])))
		assert len(result) == 3
		assert result[2][2] == True  # Endpoint reached.
		assert isinstance(result[0][1], Root)  # Intermediate is Root instance.
		assert isinstance(result[1][1], People)  # v is People instance.
		assert isinstance(result[2][1], Person)  # Endpoint is Person instance.
		assert result[2][1]() == "Hi, I'm GothAlice"
	
	def test_resolve_specific_user_action(self):
		result = list(dispatch(None, Root, deque(['user', 'GothAlice', 'foo'])))
		assert len(result) == 4
		assert result[3][2] == True  # Endpoint reached.
		assert isinstance(result[0][1], Root)  # Intermediate is Root instance.
		assert isinstance(result[1][1], People)  # v is People instance.
		assert isinstance(result[2][1], Person)  # Endpoint is Person instance.
		assert result[3][1]() == "I'm also GothAlice"
		