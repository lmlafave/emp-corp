from __future__ import division

from math import floor, ceil

from linalg import Matrix, Vector

def linspace(first, last, num=101):
	'''List of num evenly-spaced points in [first, last]'''
	diff = (last-first)/(num-1) if num > 1 else 0
	return [first + it*diff for it in range(num)]

def interp(x, y):
	'''Lowest-degree polynomial that exactly interpolates y(x)'''
	if not hasattr(x, '__len__') and not hasattr(y, '__len__'):
		return lambda x: y
	else:
		assert len(x) == len(y), 'Input and output dimensions must match'

		sys = Matrix([[xi**j for j in range(len(y))] for xi in x])
		rhs = Vector(y)

		coeffs = sys.solve(rhs)

		return lambda x: sum([ai*x**i for i, ai in enumerate(coeffs)])
