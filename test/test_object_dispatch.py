# encoding: utf-8

from __future__ import unicode_literals

import os, sys

from web.dispatch.object import ObjectDispatch

from sample import path, function  # , Simple, CallableShallow, CallableDeep, CallableMixed


# We pre-create these for the sake of convienence.
# In ordinary usage frameworks should try to avoid excessive reinstantiation where possible.
dispatch = ObjectDispatch()
promiscuous = ObjectDispatch(protect=False)


assert 'TEST_PY_VER' in os.environ, "Python version undefined? Run via tox."



class TestFunctionDispatch(object):
	def test_root_path_resolves_to_function(self):
		result = list(dispatch(None, function, path('/')))
		assert len(result) == 1
		assert result == [(None, function, True)]
		
	def test_deep_path_resolves_to_function(self):
		result = list(dispatch(None, function, path('/foo/bar/baz')))
		assert len(result) == 1
		assert result == [(None, function, True)]
