from __future__ import division

from math import sqrt, atan, sin, cos, tan

from linalg import Matrix, Vector
from helper import linspace, interp

class Blade(object):
	'''Base class for blade geometry implementations'''

	def __init__(self, d, hub_ratio, flow_coeff):
		'''Stores list of cross-sections as self.secs and extracts section points into 2d list self.pts'''
		self.rt = 0.5*d
		self.rh = hub_ratio*self.rt

		self.flow_coeff = flow_coeff

class Bamberger(Blade):
	'''Blade parameterized by NACA modified 4-digit airfoil parameters per Bamberger 2015 (https://www.mb.uni-siegen.de/iftsm/forschung/veroeffentlichungen_pdf/139_2015.pdf)'''

	def __init__(self, d, hub_ratio, flow_coeff, cd_in, k_in, tk_in, a_in, ta_in, aoa_in, sweep_in):
		'''Imports geometric parameter interpolants and delegates to Blade.__init__'''
		super(Bamberger, self).__init__(d, hub_ratio, flow_coeff)

		cd = interp(linspace(self.rh, self.rt, len(cd_in)), cd_in)
		self.c = lambda r, cd=cd: 2*r*cd(r)

		self.k = interp(linspace(self.rh, self.rt, len(k_in)), k_in)
		self.tk = interp(linspace(self.rh, self.rt, len(tk_in)), tk_in)
		self.a = interp(linspace(self.rh, self.rt, len(a_in)), a_in)
		self.ta = interp(linspace(self.rh, self.rt, len(ta_in)), ta_in)

		self.aoa = interp(linspace(self.rh, self.rt, len(aoa_in)), aoa_in)
		self.sweep = interp(linspace(self.rh, self.rt, len(sweep_in)), sweep_in)

	def gen(self, num_secs, num_pts, f=lambda t: t):  # TO-DO: rename num_pts to indicate parametricity
		'''Generate points for num_pts parameters in [0,1] at each of num_secs spanwise stations between hub and tip'''
		az0 = 0
		z0 = 0

		dr = (self.rt - self.rh)/num_secs

		pts = {'upper': [[None]*num_pts]*num_secs, 'lower': [[None]*num_pts]*num_secs}

		args = map(f, linspace(0, 1, num_pts))

		assert all([curr > prev for curr, prev in zip(args[1:], args[:-1])]), 'f(t) must increase monotonically on [0,1]'

		'''
		Later on, these points will be used to generate upper and lower surfaces for the blade. These surfaces need to extend slightly within the hub solid to ensure that a well-defined edge can be created at the root of each blade. Therefore, sections are generated beginning at 99% of the desired hub radius. This allows the final geometry to have exactly the size that the end-user expects without creating a perceptible difference in the blade topology or increasing the memory usage of this array, which already holds 3*num_secs*num_pts floating-point numbers, roughly 26 kiB.
		'''

		for i, r in enumerate(linspace(0.99*self.rh, self.rt, num_secs)):
			sweep = self.sweep(r)
			aoa = self.aoa(r)

			twist = aoa + atan(self.flow_coeff*self.rt/(r*(1 - (self.rh/self.rt)**2)))
			turn = tan(sweep)*dr

			az0 += turn*cos(twist)/r
			z0 += turn*sin(twist)

			curves = self.sec(r).profile

			orig = self.sec(r).centroid()
			shift = lambda pos: tuple([x - x0 for x, x0 in zip(pos, orig)])

			for (key, lol) in pts.items():
				az = lambda u, w: az0 - (u*cos(twist) + w*sin(twist))/r
				z = lambda u, w: z0 - u*sin(twist) + w*cos(twist)

				x = lambda u, w: r*cos(az(u, w))
				y = lambda u, w: r*sin(az(u, w))

				lol[i] = [(x(u, w), y(u, w), z(u, w)) for u, w in map(shift, map(curves[key], args))]

		return pts

	def sec(self, r):
		'''Interpolates geometric parameters and returns evenly-spaced profiles'''
		return NACA4m(self.c(r), self.k(r), self.tk(r), self.a(r), self.ta(r))

class Section(object):
	'''Base class for section geometry implementations'''

	def __init__(self, c):
		'''Initializes base Section with child-defined boundary functions'''
		self.c = c
		self.profile = self.bounds()

	def qc(self):
		'''Section quarter-chord for spanwise positioning'''
		return 0.25*self.c

	def centroid(self, num_t=101, step=1e-4):  # TO-DO: improve efficiency via higher-order computation
		'''Compute numerical centroid of general section'''
		usum = 0
		wsum = 0

		count = 0

		for i, ((utop, wtop), (ubot, wbot)) in enumerate(zip(*[map(curve, linspace(0, 1, num_t)) for curve in self.profile.values()])):
			dist = sqrt((ubot - utop)**2 + (wbot - wtop)**2)

			num_steps = int(dist/step)

			usum += sum(linspace(utop, ubot, num_steps))
			wsum += sum(linspace(wtop, wbot, num_steps))

			count += num_steps

		return (usum/count, wsum/count)

class NACA4m(Section):
	'''Section implementation for 4-digit modified NACA airfoil'''

	def __init__(self, c, k, tk, a, ta):
		'''Imports geometric parameters and delegates to Section.__init__'''
		self.k = k
		self.tk = tk

		self.a = a
		self.ta = ta

		super(NACA4m, self).__init__(c)

	def bounds(self):
		'''Returns functions that bound self'''
		uc = lambda t: self.c*t

		def wc(t):
			if t < self.tk:
				return self.c*self.k*(2*self.tk*t - t**2)/self.tk**2
			else:
				return self.c*self.k*(1 - 2*self.tk + 2*self.tk*t - t**2)/(1 - self.tk)**2

		def m(t):
			if t < self.tk:
				return 2*self.k/self.tk**2 * (self.tk - t)
			else:
				return 2*self.k/(1 - self.tk)**2 * (self.tk - t)

		coeffs = NACA4m.coeffs(self.a, self.ta)

		def h(t):
			if t < self.ta:
				return self.c*sum([coeffs[0]*sqrt(t)] + [ai*t**(i+1) for i, ai in enumerate(coeffs[1:4])])
			else:
				return self.c*sum([di*(1-t)**i for i, di in enumerate(coeffs[4:])])

		return {'upper': lambda t: (uc(t) - h(t)*sin(atan(m(t))), wc(t) + h(t)*cos(atan(m(t)))), 'lower': lambda t: (uc(t) + h(t)*sin(atan(m(t))), wc(t) - h(t)*cos(atan(m(t))))}

	@staticmethod
	def coeffs(a, ta):
		'''Coefficients of piecewise-quadratic thickness distribution from geometric parameters per Abbott 1959, p. 117 (https://aeroknowledge77.files.wordpress.com/2011/09/58986488-theory-of-wing-sections-including-a-summary-of-airfoil-data.pdf)'''
		a0 = sqrt(2.2038)*a
		d0 = 0.01*a

		d1 = NACA4m.d1(a, ta)

		sys = Matrix([[ta, ta**2, ta**3, 0, 0],
		             [0, 0, 0, (1-ta)**2, (1-ta)**3],
		             [1, 2*ta, 3*ta**2, 0, 0],
		             [0, 0, 0, 2*(1-ta), 3*(1-ta)**2],
		             [0, 2, 6*ta, -2, 6*(1-ta)]])
		rhs = Vector([a-sqrt(ta)*a0, a-d0-(1-ta)*d1, -0.5*a0/sqrt(ta), -d1, 0.25*a0/sqrt(ta**3)])
		a1, a2, a3, d2, d3 = sys.solve(rhs)

		return [a0, a1, a2, a3, d0, d1, d2, d3]

	@staticmethod
	def d1(a, ta):
		'''Aft linear coefficient by interpolation between known values per Abbott 1959, p. 117'''
		ta_th = linspace(0.2, 0.6, 5)
		ratio_th = [1, 1.17, 1.575, 2.325, 3.5]

		f = interp(ta_th, ratio_th)
		return a*f(ta)
