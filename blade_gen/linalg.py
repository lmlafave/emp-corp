from __future__ import division, print_function
from operator import *

class Matrix(object):
	'''Implementation for 2d dense matrix'''

	def __init__(self, dat = None):
		'''Initializes self by storing entries as self.dat and computing number of rows self.m and number of columns self.n'''
		self.m = len(dat) if hasattr(dat, '__len__') else int(dat is not None)
		self.n = len(dat[0]) if hasattr(dat[0], '__len__') else int(dat[0] is not None)

		self.dat = list([list(row) for row in dat])  # TO-DO: polish this up, time permitting

	def __len__(self):
		'''Total number of entries in self'''
		return sum([len(row) for row in self.dat])

	def __getitem__(self, inds):
		'''Value at row i, column j'''
		return self.dat[inds[0]][inds[1]]

	def __setitem__(self, inds, val):
		'''Set value at row i, column j to val'''
		self.dat[inds[0]][inds[1]] = val

	def __str__(self):
		'''Prints contents of self'''
		return [str(row) + '\n' for row in dat]

	def __mul__(self, x):
		'''Product of self and x if the operation is well-defined'''
		if isinstance(x, int) or isinstance(x, float):
			return self._mul_const(x)
		if isinstance(x, Vector):
			return self._mul_vec(x)

	def __truediv__(self, x):
		'''Quotient of self and x if well-defined'''
		if isinstance(x, int) or isinstance(x, float):
			return self._div_const(x)

	def __rtruediv__(self, x):
		'''Product of x and self.inv() if well-defined'''
		if isinstance(x, Vector):
			return self.solve(x)

	# def __pow__(self, n):  # WIP
	# 	if n < 0:
	# 		return self.inv()*self**(-n)
	# 	else if n > 1:
	# 		return self*self**(n-1)
	# 	else:
	# 		return self

	# def __iter__(self):  # WIP
	# 	'''Initializes iterator for self as iterator through self.dat'''
	# 	return iter(self.dat[0])
	#
	# def __next__(self):
	# 	'''Increments iterator through elements of self in row-major order'''
	# 	try:
	# 		return next(self.dat)
	# 	except StopIteration:
	# 		return iter(self.dat[])

	def _mul_const(self, c):
		'''Scalar product of self and c'''
		return Matrix([[float(c)*it for it in row] for row in self.dat])

	def _mul_vec(self, b):
		'''Vector product of self and b'''
		return Vector([sum([row[j]*b[j] for j in range(len(b))]) for row in self.dat])

	def _div_const(self, c):
		'''Scalar quotient of self and c'''
		return Matrix([[it/float(c) for it in row] for row in self.dat])

	def is_square(self):
		'''True if self has the same number of rows and columns, False otherwise'''
		return self.m == self.n

	def transpose(self):
		'''Transpose of self as new Matrix'''
		return Matrix([[self[j,i] for j in range(self.n)] for i in range(self.m)])

	def sub(self, i, j):
		'''Submatrix of self formed by removing row i and column j'''
		return Matrix([[self[k+int(k>=i), l+int(l>=j)] for l in range(self.n-1)] for k in range(self.m-1)])

	def minor(self, i, j):
		'''Minor of self at index (i, j)'''
		return self.sub(i, j).det()

	def cofactor(self, i, j):
		'''Cofactor of self at index (i, j)'''
		return (-1)**(i+j) * self.minor(i, j)

	def det(self):
		'''Determinant of self'''
		assert self.is_square(), 'Determinant of a non-square matrix is undefined'

		if self.m == 1 and self.n == 1:
			return self[0,0]
		else:
			return sum([self[0,i] * self.cofactor(0, i) for i in range(self.n)])

	def adj(self):
		'''Returns adjoint (i.e. transpose of cofactor matrix) of self'''
		return Matrix([[self.cofactor(i, j) for j in range(len(self.dat[i]))] for i in range(len(self.dat))]).transpose()

	def inv(self):
		'''Returns inverse of self'''
		return self.adj() / self.det()

	def solve(self, b):
		'''Solves linear system self*x=b for x'''
		return self.inv() * b

class Vector(Matrix):
	'''Implementation for Vector as 1d Matrix'''

	def __init__(self, dat = None):
		'''Initializes self by storing dat and computing number of entries m'''
		self.dat = list(dat) if hasattr(dat, "__len__") else dat
		self.m = len(dat) if hasattr(dat, "__len__") else dat is not None

	def __len__(self):
		'''Returns number of entries in self'''
		return len(self.dat)

	def __getitem__(self, i):
		'''Gets ith entry in self'''
		return self.dat[i]

	def __setitem__(self, i, val):
		'''Sets ith entry in self to val'''
		self.dat[i] = val

	def __str__(self):
		'''Prints data stored in self'''
		return str(self.dat)

	def __iter__(self):
		'''Initializes iterator for self as iterator through self.dat'''
		return iter(self.dat)

	def __next__(self):
		'''Increments iterator for self by stepping through self.dat'''
		return next(self.dat)
