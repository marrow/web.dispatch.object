# encoding: utf-8

from __future__ import unicode_literals

import os
import warnings

from web.dispatch.object import ObjectDispatch
from web.dispatch.object.util import nodefault

from sample import path, function, Simple, CallableShallow, CallableDeep, CallableMixed


# We pre-create these for the sake of convienence.
# In ordinary usage frameworks should try to avoid excessive reinstantiation where possible.
dispatch = ObjectDispatch()
promiscuous = ObjectDispatch(protect=False)


assert 'TEST_PY_VER' in os.environ, "Python version undefined? Run via tox."


def test_nodefault_repr():
	assert repr(nodefault) == "<no value>"



if __debug__:
	class TestFallbackBehaviour(object):
		def test_string_value(self):
			with warnings.catch_warnings(record=True) as w:
				warnings.simplefilter("always")
				
				result = list(dispatch(None, function, '/'))
				
				assert len(w) == 1
				assert issubclass(w[-1].category, RuntimeWarning)
				assert 'production' in str(w[-1].message)
				
				assert len(result) == 1
		
		def test_list_value(self):
			with warnings.catch_warnings(record=True) as w:
				warnings.simplefilter("always")
				
				result = list(dispatch(None, function, ['foo', 'bar']))
				
				assert len(w) == 1
				assert issubclass(w[-1].category, RuntimeWarning)
				assert 'production' in str(w[-1].message)
				
				assert len(result) == 1


class TestFunctionDispatch(object):
	def test_root_path_resolves_to_function(self):
		result = list(dispatch(None, function, path('/')))
		assert len(result) == 1
		assert result == [(None, function, True)]
		
	def test_deep_path_resolves_to_function(self):
		result = list(dispatch(None, function, path('/foo/bar/baz')))
		assert len(result) == 1
		assert result == [(None, function, True)]


class TestSimpleDispatch(object):
	def test_protected_init_method(self):
		result = list(dispatch(None, Simple, path('/__init__')))
		assert len(result) == 1
		
		assert result[0][0] == None
		assert isinstance(result[0][1], Simple)
		assert result[0][2] == False
	
	def test_protected_simple_value(self):
		result = list(dispatch(None, Simple, path('/_protected')))
		assert len(result) == 1
		
		assert result[0][0] == None
		assert isinstance(result[0][1], Simple)
		assert result[0][2] == False
	
	def test_static_attribute(self):
		result = list(dispatch(None, Simple, path('/static')))
		assert len(result) == 2
		
		assert result[0][0] == None
		assert isinstance(result[0][1], Simple)
		assert result[0][2] == False
		
		assert result[1] == ("static", "foo", True)
	
	def test_shallow_class_lookup(self):
		result = list(dispatch(None, Simple, path('/foo')))
		assert len(result) == 2
		
		assert result[0][0] == None
		assert isinstance(result[0][1], Simple)
		assert result[0][2] == False
		
		assert result[1][0] == "foo"
		assert isinstance(result[1][1], Simple.foo)
		assert result[1][2] == True
	
	def test_deep_class_lookup(self):
		result = list(dispatch(None, Simple, path('/foo/bar')))
		assert len(result) == 3
		
		assert result[0][0] == None
		assert isinstance(result[0][1], Simple)
		assert result[0][2] == False
		
		assert result[1][0] == "foo"
		assert isinstance(result[1][1], Simple.foo)
		assert result[1][2] == False
		
		assert result[2][0] == "bar"
		assert isinstance(result[2][1], Simple.foo.bar)
		assert result[2][2] == True
	
	def test_partial_incomplete_lookup(self):
		result = list(dispatch(None, Simple, path('/foo/bar/diz')))
		assert len(result) == 3
		
		assert result[0][0] == None
		assert isinstance(result[0][1], Simple)
		assert result[0][2] == False
		
		assert result[1][0] == "foo"
		assert isinstance(result[1][1], Simple.foo)
		assert result[1][2] == False
		
		assert result[2][0] == "bar"
		assert isinstance(result[2][1], Simple.foo.bar)
		assert result[2][2] == False
	
	def test_deepest_endpoint_lookup(self):
		result = list(dispatch(None, Simple, path('/foo/bar/baz')))
		assert len(result) == 4
		
		assert result[0][0] == None
		assert isinstance(result[0][1], Simple)
		assert result[0][2] == False
		
		assert result[1][0] == "foo"
		assert isinstance(result[1][1], Simple.foo)
		assert result[1][2] == False
		
		assert result[2][0] == "bar"
		assert isinstance(result[2][1], Simple.foo.bar)
		assert result[2][2] == False
		
		assert result[3][0] == "baz"
		assert result[3][1]() == "baz"
		assert result[3][2] == True


class TestCallableShallowDispatch(object):
	def test_root_path_resolves_to_instance(self):
		result = list(dispatch(None, CallableShallow, path('/')))
		assert len(result) == 1
		
		assert result[0][0] == None
		assert isinstance(result[0][1], CallableShallow)
		assert result[0][2] == True
		
	def test_deep_path_resolves_to_instance(self):
		result = list(dispatch(None, CallableShallow, path('/foo/bar/baz')))
		assert len(result) == 1
		
		assert result[0][0] == None
		assert isinstance(result[0][1], CallableShallow)
		assert result[0][2] == True


class TestCallableDeepDispatch(object):
	'''
	class CallableDeep:
	__init__ = init
	
	class foo:
		__init__ = init
		
		class bar:
			__init__ = init
			
			def __call__(self, method):
				return method
	
	'''
	def test_shallow_class_lookup(self):
		result = list(dispatch(None, CallableDeep, path('/foo')))
		assert len(result) == 2
		
		assert result[0][0] == None
		assert isinstance(result[0][1], CallableDeep)
		assert result[0][2] == False
		
		assert result[1][0] == "foo"
		assert isinstance(result[1][1], CallableDeep.foo)
		assert result[1][2] == True
	
	def test_deep_callable_class_lookup(self):
		result = list(dispatch(None, CallableDeep, path('/foo/bar')))
		assert len(result) == 3
		
		assert result[0][0] == None
		assert isinstance(result[0][1], CallableDeep)
		assert result[0][2] == False
		
		assert result[1][0] == "foo"
		assert isinstance(result[1][1], CallableDeep.foo)
		assert result[1][2] == False
		
		assert result[2][0] == "bar"
		assert isinstance(result[2][1], CallableDeep.foo.bar)
		assert result[2][2] == True
	
	def test_incomplete_lookup(self):
		result = list(dispatch(None, CallableDeep, path('/foo/diz')))
		assert len(result) == 2
		
		assert result[0][0] == None
		assert isinstance(result[0][1], CallableDeep)
		assert result[0][2] == False
		
		assert result[1][0] == "foo"
		assert isinstance(result[1][1], CallableDeep.foo)
		assert result[1][2] == False
	
	def test_beyond_callable_class_lookup(self):
		result = list(dispatch(None, CallableDeep, path('/foo/bar/baz')))
		assert len(result) == 3
		
		assert result[0][0] == None
		assert isinstance(result[0][1], CallableDeep)
		assert result[0][2] == False
		
		assert result[1][0] == "foo"
		assert isinstance(result[1][1], CallableDeep.foo)
		assert result[1][2] == False
		
		assert result[2][0] == "bar"
		assert isinstance(result[2][1], CallableDeep.foo.bar)
		assert result[2][2] == True


class TestCallableMixedDispatch(object):
	'''
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
	'''
	def test_shallow_class_lookup(self):
		result = list(dispatch(None, CallableMixed, path('/foo')))
		assert len(result) == 2
		
		assert result[0][0] == None
		assert isinstance(result[0][1], CallableMixed)
		assert result[0][2] == False
		
		assert result[1][0] == "foo"
		assert isinstance(result[1][1], CallableMixed.foo)
		assert result[1][2] == True
	
	def test_deep_callable_class_lookup(self):
		result = list(dispatch(None, CallableMixed, path('/foo/bar')))
		assert len(result) == 3
		
		assert result[0][0] == None
		assert isinstance(result[0][1], CallableMixed)
		assert result[0][2] == False
		
		assert result[1][0] == "foo"
		assert isinstance(result[1][1], CallableMixed.foo)
		assert result[1][2] == False
		
		assert result[2][0] == "bar"
		assert isinstance(result[2][1], CallableMixed.foo.bar)
		assert result[2][2] == True
	
	def test_incomplete_lookup(self):
		result = list(dispatch(None, CallableMixed, path('/foo/diz')))
		assert len(result) == 2
		
		assert result[0][0] == None
		assert isinstance(result[0][1], CallableMixed)
		assert result[0][2] == False
		
		assert result[1][0] == "foo"
		assert isinstance(result[1][1], CallableMixed.foo)
		assert result[1][2] == False
	
	def test_deepest_endpoint_lookup(self):
		result = list(dispatch(None, CallableMixed, path('/foo/bar/baz')))
		assert len(result) == 4
		
		assert result[0][0] == None
		assert isinstance(result[0][1], CallableMixed)
		assert result[0][2] == False
		
		assert result[1][0] == "foo"
		assert isinstance(result[1][1], CallableMixed.foo)
		assert result[1][2] == False
		
		assert result[2][0] == "bar"
		assert isinstance(result[2][1], CallableMixed.foo.bar)
		assert result[2][2] == False
		
		assert result[3][0] == "baz"
		assert result[3][1]() == 'baz'
		assert result[3][2] == True
