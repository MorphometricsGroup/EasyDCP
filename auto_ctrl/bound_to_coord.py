#rotates chunks' bounding box in accordance of coordinate system for active chunk
#bounding box size is kept 
#compatibility: Agisoft Metashape Professional 1.3.0

import Metashape, math

doc = Metashape.app.document
chunk = doc.chunk

T = chunk.transform.matrix

v_t = T * Metashape.Vector( [0,0,0,1] )
v_t.size = 3

if chunk.crs:
	m = chunk.crs.localframe(v_t)
else:
	m = Metashape.Matrix().Diag([1,1,1,1])

m = m * T

s = math.sqrt(m[0,0] ** 2 + m[0,1] ** 2 + m[0,2] ** 2) #scale factor

R = Metashape.Matrix( [[m[0,0],m[0,1],m[0,2]], [m[1,0],m[1,1],m[1,2]], [m[2,0],m[2,1],m[2,2]]])

R = R * (1. / s)

reg = chunk.region
reg.rot = R.t()
chunk.region = reg