# Import features from Python 3
from __future__ import division

# Import standard libraries and classes
import sys
import os

from math import pi

from System import Array

# Import SpaceClaim API classes
from SpaceClaim.Api.V18.Geometry import Knot
from SpaceClaim.Api.V18.Geometry import NurbsData
from SpaceClaim.Api.V18.Geometry import ControlPoint

# Import user classes
sys.path.append(os.path.abspath("C:/Users/llafave/Documents/GitHub/blade-lib"))
from blade import Bamberger
from helper import linspace

# Define functions requiring the SpaceClaim API
def make(blade):
    mcurves = {}
    msurfs = {}
    mbods = {}

    dbods = {}

    # Generate blade upper and lower surfaces
    for key in ('upper', 'lower'):
        pts = [List[Point]([Point.Create(*pos) for pos in row]) for row in blade.pts[key]]

        mcurves[key] = [NurbsCurve.CreateThroughPoints(False, row, 0.01) for row in pts]

        vcurves = [NurbsCurve.CreateThroughPoints(False, [spl.ControlPoints[i].Position for spl in mcurves[key]], 0.01) for i in range(len(mcurves[key][0].ControlPoints))]

        msurfs[key] = fit_surf(mcurves[key])

        dom = BoxUV.Create(Interval.Create(0, 1), Interval.Create(0, 1))
        mbods[key] = Body.CreateSurfaceBody(msurfs[key], dom)
        dbods[key] = DesignBody.Create(GetActivePart(), key, mbods[key])

#    sel_start = Selection.CreateByObjects(dbods['lower'].Faces[0])
#    sel_end = Selection.CreateByObjects(dbods['upper'].Faces[0])
#    dbods['blade'] = ExtrudeFaces.UpTo(sel_start, Direction.DirZ, sel_end, Point.Create(MM(112.196881687354), MM(-14.8215953241441), MM(4.95815239135508)), ExtrudeFaceOptions()).CreatedBodies[0]

#    sel_del = Selection.CreateByNames('upper')
#    Delete.Execute(sel_del)

#    del dbods['upper'], dbods['lower']

    pt_bot = Point.Create(0, 0, -0.5*blade.h)
    pt_top = Point.Create(0, 0, 0.5*blade.h)
    pt_out = Point.Create(blade.r[0], 0, 0.5*blade.h)
    dbods['hub'] = CylinderBody.Create(pt_bot, pt_top, pt_out).CreatedBodies[0]

#    sel_start = Selection.CreateByObjects(dbods['blade'].Faces[0])
#    sel_end = Selection.CreateByObjects(dbods['hub'].Faces[0])
#    ExtrudeFaces.UpTo(sel_start, -Direction.DirX, sel_end, Point.Create(blade.r[0], 0, 0), ExtrudeFaceOptions())

    Selection.Clear()

def fit_surf(usplines):
    urank = len(usplines[0].ControlPoints)
    assert all([len(spl.ControlPoints) == urank for spl in usplines]), 'Interpolation between unlike splines is undefined'

    vpts = [[spl.ControlPoints[i].Position for spl in usplines] for i in range(urank)]
    vsplines = [NurbsCurve.CreateThroughPoints(False, row, 0.01) for row in vpts]
    vrank = len(vsplines[0].ControlPoints)
    assert all([len(spl.ControlPoints) == vrank for spl in vsplines]), 'Interpolation between unlike splines is undefined'

    udat = usplines[0].Data
    vdat = vsplines[0].Data

    cp = Array.CreateInstance(ControlPoint, len(usplines), urank)
    for i, spl in enumerate(usplines):
        for j, pt in enumerate(spl.ControlPoints):
            cp[i,j] = pt

    return NurbsSurface.Create(udat, vdat, cp)

# Generate knots per f(t) on t ∈ [0,1]
def knot_arr(deg, rank, f=lambda t: t, mults=None):
    ord = deg + 1
    num = rank + ord

    mults = [ord] + [1]*(num-2*ord) + [ord] if mults is None else mults

    t = linspace(0, 1, len(mults))
    vals = [f(val) for val in t]
	print(vals)

    return Array[Knot]([Knot(v, m) for (v, m) in zip(vals, mults)])

# Clear the model window
ClearAll()

# Read and collate model Parameters
d = Parameters.dia
ν = Parameters.hub_tip_ratio

h = Parameters.len

cd = [Parameters.chord_hub, Parameters.chord_mid, Parameters.chord_tip]  # diameter-normalized chord
a = [Parameters.max_thick_hub, Parameters.max_thick_mid, Parameters.max_thick_tip]  # chord-normalized max thickness
ua = [Parameters.argmax_thick_hub, Parameters.argmax_thick_mid, Parameters.argmax_thick_tip]  # chord-normalized position of max thickness
k = [Parameters.max_camb_hub, Parameters.max_camb_mid, Parameters.max_camb_tip]  # chord-normalized max camber
uk = [Parameters.argmax_camb_hub, Parameters.argmax_camb_mid, Parameters.argmax_camb_tip]  # chord-normalized position of max camber
aoa = [Parameters.aoa_hub, Parameters.aoa_1q, Parameters.aoa_mid, Parameters.aoa_3q, Parameters.aoa_tip]  # angle of attack
sweep = [Parameters.sweep_hub, Parameters.sweep_mid, Parameters.sweep_tip]  # sweep angle

# Create Blade object per Bamberger 2015 (https://www.mb.uni-siegen.de/iftsm/forschung/veroeffentlichungen_pdf/139_2015.pdf)
blade = Bamberger(d, ν, h, cd, k, uk, a, ua, aoa, sweep, num_secs=11, num_pts=101)  # FAILS

# Generate blade solid in model window
make(blade)
