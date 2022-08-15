from __future__ import division

from math import sin, cos, tan, atan

from linalg import Matrix, Vector
from helper import dot, prod

class Curve(object):
	def __init__(self, funcs):
		if not hasattr(funcs, '__len__'):
			self.funcs = [funcs]
		else:
			self.funcs = list(funcs)

		self.dim = len(funcs)

	def __call__(self, t):
		return (f(t) for f in funcs)

	def int(self, a, b=None, num_pts=None):
		'''Returns a- or (analytic or num_pts-numeric) [a,b]-bounded integral'''
		if b is None:
			return self._int_1b(a)
		else:
			return self._int_2b(a, b, num_pts)

class Function(object):
	'''Parent class for functions to implement integration, fallback {+,*} to form {Sum,Product} if child fails to define {+,*}'''

	def __init__(self, order = None):
		'''Stores order of function to determine compatibility for addition'''
		self.order = order

	def __add__(self, other):
		'''Returns Sum of Function self and Function others'''
		return Sum([self, other])

	def __mul__(self, other):
		'''Returns Product of Function self and Function others'''
		return Product([self, other])

	def _int_trap(self, a, b, num):
		'''Computes trapezoidal [a,b]-bounded Riemann integral'''
		x = linspace(a, b, num)
		return sum([0.5*(self(x[i-1])+self(x[i])) * (x[i]-x[i-1]) for i in range(1, num)])

	def _int_1b(self, a):
		'''Returns definite integral of self with lower bound a'''
		F = self.antiderivative()
		return Constant(-F(a)) + F

	def _int_2b(self, a, b, num_pts = None):
		'''Compute analytic [a,b]-bounded integral if self.antiderivative() is defined else num_pts-numeric'''
		if num_pts is None and hasattr(self, 'antiderivative'):
			F = self.antiderivative()
			return F(b) - F(a)
		else:
			return self._int_trap(a, b, 101 if num_pts is None else num_pts)

	def int(self, a, b = None, num_pts = None):
		'''Returns a- or (analytic or num_pts-numeric) [a,b]-bounded integral'''
		if b is None:
			return self._int_1b(a)
		else:
			return self._int_2b(a, b, num_pts)

class Sum(Function):
	'''Implementation for summation of Functions'''

	def __init__(self, funcs, **kwargs):
		'''Stores list of Function addends as self.funcs'''
		self.funcs = list(funcs)
		super(Sum, self).__init__(**kwargs)

	def __call__(self, t):
		'''Evaluates Sum as sum of sub-function evaluations'''
		return sum([f(t) for f in self.funcs])

	def antiderivative(self):
		'''Returns functional antiderivative of Sum as sum of sub-function antiderivatives'''
		return sum([it.antiderivative() for it in self.funcs])

class Product(Function):
	'''Implementation for product of Functions'''

	def __init__(self, funcs):
		'''Stores list of Function factors as self.funcs'''
		self.funcs = list(funcs)
		super(Product, self).__init__()

	def __call__(self, t):
		'''Evaluates Product as product of sub-function evaluations'''
		return prod([f(t) for f in self.funcs])

class Composite(Function):
	'''Implementation for Function with Function as its argument'''

	def __init__(self, base, arg):
		'''Initialize with inner function as self.func and outer function as self.arg'''
		self.func = func
		self.arg = arg

	def __call__(t):
		'''Evaluate self by evaluating self.arg recursively'''
		return self.base(self.arg(t))

class Piecewise(Function):
	''''''

	def __init__(self, funcs, bounds, **kwargs):
		''''''
		if not hasattr(bounds, "__len__"):
			bounds = [bounds]

		assert len(bounds) == len(funcs) - 1, 'Incorrect number of bounds for len(funcs)-piecewise function'

		self.funcs = list(funcs)
		self.bounds = list(bounds)

		super(Piecewise, self).__init__(**kwargs)

	def __call__(t):
		''''''
		for i, t0 in enumerate(self.bounds):
			if t0 > t:
				return self.funcs[i](t)
		return self.funcs[-1](t)

	# def is_cont(ord=0, t=None):
	# 	assert isinstance(ord, 'int'), 'Order of continuity must be an integer'
	#
	# 	if ord == 0:
	# 		if t is None:
	# 			return all([self.funcs[i](t0) == self.funcs[i+1](t0) for i, t0 in enumerate(bounds)])
	# 		else:
	# 			return self(t) == all([self.funcs[i+1](t) for i, t0 in enumerate(self.bounds) if t0 == min([abs(it - t0) for it in self.bounds])])
	# 	else:
	# 		return self.derivative().is_cont(ord-1)
	#
	# 	if t is None:
	# 		return (self.is_cont(ord-1, t) or ord == 0) and all([self.funcs[i](t0) == self.funcs[i+1](t0) for i, t0 in enumerate(bounds)])
	# 	else:
	# 		return self(t0)
	#
	# def is_c1(t=None):
	# 	return self.is_cont(1, t)
	#
	# def is_c2(t=None):
	# 	return self.is_cont(2, t)

	def antiderivative(self):
		''''''
		return Piecewise([Constant(sum(self.funcs[:i](bound[i-1]))) + f.antiderivative() for i, f in enumerate(self.funcs)], bounds)

class Sin(Function):
	'''Implementation for sine with variable frequency and phase shift'''

	def __init__(self, freq=1, phase=0):
		'''Stores frequency as self.freq and phase shift as self.phase'''
		self.freq = freq
		self.phase = phase

	def __call__(self, t):
		'''Value of self at t'''
		return sin(self.freq*t + self.phase)

class Cos(Function):
	'''Implementation for cosine with variable frequency and phase shift'''

	def __init__(self, freq=1, phase=0):
		'''Stores frequency as self.freq and phase shift as self.phase'''
		self.freq = freq
		self.phase = phase

	def __call__(self, t):
		'''Value of self at t'''
		return cos(self.freq*t + self.phase)

class Tan(Function):
	'''Implementation for tangent with variable frequency and phase shift'''

	def __init__(self, freq=1, phase=0):
		'''Stores frequency as self.freq and phase shift as self.phase'''
		self.freq = freq
		self.phase = phase

	def __call__(self, t):
		'''Value of self at t'''
		return tan(self.freq*t + self.phase)

class Atan(Function):
	'''Implementation for arctangent'''

	def __init__(self):
		pass

	def __call__(self, t):
		return atan(t)

class Power(Function):
	'''Implementation for exponentiation as coeff*(x**pow)'''

	def __init__(self, coeff, pow):
		'''Initializes self by storing coefficient as self.coeff and exponent as self.pow'''
		self.coeff = coeff
		self.pow = pow
		super(Power, self).__init__(pow)

	def __str__(self):
		'''Prints self as "<a>x**<b>"'''
		return str(self.coeff) + "x**" + str(self.pow)

	def __call__(self, t=None):
		'''Evaluates self at t'''
		if t is None and self.pow == 0:
			return self.coeff
		else:
			return self.coeff * pow(t, self.pow)

	def antiderivative(self):
		'''Returns functional antiderivative of self as Power'''
		return Power(self.coeff/(1+self.pow), 1+self.pow)

class Root(Power):
	'''Implementation for nth root as (1/n)th Power'''

	def __init__(self, coeff, ord):
		'''Initializes self as Power with exponent 1/ord'''
		super(Root, self).__init__(coeff, 1/ord)

class Sqrt(Root):
	'''Shorthand for square-root Function'''

	def __init__(self, coeff):
		'''Initializes self as Root of order 2'''
		super(Sqrt, self).__init__(coeff, 2)

class Constant(Power):
	'''Implementation for constant-valued Function'''

	def __init__(self, val):
		'''Initializes self as Power with exponent 0'''
		super(Constant, self).__init__(val, 0)

class Polynomial(Sum):
	'''Implementation for polynomial Function as Sum of Powers'''

	def __init__(self, coeffs):
		'''Initializes self as Sum of Powers and stores polynomial degree in self.deg and coeffs in self.coeffs'''
		self.deg = len(coeffs) - 1
		self.coeffs = list(coeffs)
		super(Polynomial, self).__init__([Power(coeffs[i], i) for i in range(len(coeffs))])

	def __str__(self):
		'''Prints self, all pretty like'''
		out = None
		for i, coeff in enumerate(self.coeffs):
			if not coeff == 0:
				if out is None:
					out = str(coeff)
				else:
					out += " - " if coeff < 0 else " + "
					if not abs(coeff == 1):
						out += str(abs(coeff))
				if i > 0:
					out += "x"
				if i > 1:
					out += "**" + str(i)
		return out

	def antiderivative(self):
		'''Computes antiderivative of self as sum of antiderivatives of self.funcs'''
		return Polynomial([0] + [coeff/(i+1) for i, coeff in enumerate(self.coeffs)])

	@staticmethod
