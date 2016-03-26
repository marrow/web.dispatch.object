# encoding: utf-8

try:
	str = unicode
	range = xrange
except:
	str = str
	range = range


class NoDefault(object):
	__slots__ = []
	
	def __repr__(self):
		return "<no value>"

nodefault = NoDefault()  # Sentinel value.


def ipeek(d):
	"""Iterate through a deque, popping elements from the left after they have been seen."""
	last = None
	
	# We eat trailing slashes.  No sir, can't say we like 'em.
	while d and d[-1] == '':
		d.pop()
	
	while d:
		yield last, d[0]
		last = d.popleft()
