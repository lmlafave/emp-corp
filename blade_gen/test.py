from blade import Bamberger
from helper import linspace

import dis

def test_381_init():
	d = 0.381
	ν = 0.387

	cd = [0.33, 0.13, 0.12]
	a = [0.12, 0.05, 0.051]
	ta = [0.13, 0.1, 0.33]
	k = [0, 0.056, 0.059]
	tk = [0.7, 0.2, 0.56]
	α = [0, 0.0855, 0.0681, 0.0297, 0]
	λ = [0.209, -0.279, 0.768]

	c = [cdi*di for (cdi, di) in zip(cd, linspace(ν*d, d, len(cd)))]

	blade = Bamberger(d, ν, cd, a, ta, k, tk, α, λ)

	# Check chord length
	assert round(blade.section(blade.rh).c, 6) == round(c[0], 6)
	assert round(blade.section(blade.rt).c, 6) == round(c[-1], 6)

	# Check (u, w) at known locations on hub
	prof = blade.profile(blade.rh)
	assert prof['upper'](0.1) != prof['lower'](0.1)  # :)

tests = [test_381_init]

[case() for case in tests]
