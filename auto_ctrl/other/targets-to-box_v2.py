# Project to automate Agisoft Process
# Automation of the floor alignment and setting the correct bounding box.
# Assembled/Written by: Richard Garsthagen - www.pi3dscan.com
# Modified by Alex Feldman, UTokyo Field Phenomics Lab for plant phenotyping
# for instructions on how to use see: http://www.pi3dscan.com/index.php/instructions/item/agisoft-how-to-process-a-scan-with-projection

#      ------------ p1
#   |
#   |   (plants)
#   |
#   p0 ------------ 

import Metashape
import math

def update_boundbox():

    doc = Metashape.app.document
    chunk = doc.chunk     # This points to the first chunk!

    #ground targets for finding horizontal center
    p0 = "target 1"  
    p1 = "target 8"  

    fp0 = fp1 = 0

    #setting for Y up, Z forward -> needed for mixamo/unity

    c = 0

    #find center points (my way)
    c1=0
    c2=0

    print (p0,p1)
    for m in chunk.markers:
        if m.label == p0:
            c1=c
            fp0=1
        elif m.label == p1:
            c2=c
            fp1=1
        c=c+1

    #check markers found (my way)
    if fp0 and fp1:
      print ("Found all markers")
      print (c1,c2)
      chunk.updateTransform()
    else:
      print ("Error: not all markers found")
      print(fp0,fp1)

    newregion = chunk.region

    T = chunk.transform.matrix
    #v_t = T * Metashape.Vector( [0,0,0,1] )
    m = Metashape.Matrix().Diag([1,1,1,1])	

    m = m * T
    s = math.sqrt(m[0,0] ** 2 + m[0,1] ** 2 + m[0,2] ** 2) #scale factor
    R = Metashape.Matrix( [[m[0,0],m[0,1],m[0,2]], [m[1,0],m[1,1],m[1,2]], [m[2,0],m[2,1],m[2,2]]])
    R = R * (1. / s)
    newregion.rot = R.t()

    # Calculate center point of the bounding box, by taking the average of 2 left and 2 right markers 
    mx = (chunk.markers[c1].position + chunk.markers[c2].position) / 2 #my way 

    print('x',chunk.markers[c2].position[0],chunk.markers[c1].position[0])
    print('y',chunk.markers[c2].position[1],chunk.markers[c1].position[1])
    box_X_length = math.fabs(chunk.markers[c2].position[0] - chunk.markers[c1].position[0]) #x-axis. may return negative number, so absoluted
    box_Y_length = math.fabs(chunk.markers[c2].position[1] - chunk.markers[c1].position[1]) #y-axis. may return negative number, so absoluted
    
    print('lengths:',box_X_length,box_Y_length)
    
    if box_Y_length > box_X_length:
        swap_length = box_X_length
        box_X_length = box_Y_length
        box_Y_length = swap_length
    
    box_Z_length = box_Y_length#chunk.markers[c2].position[2] - chunk.markers[c1].position[2] #z-axis. same as Y length

    print('lengths:',box_X_length,box_Y_length,box_Z_length)

    Z_ratio = 4 #my way. Change this to adjust box height (default=1)

    mx = Metashape.Vector([mx[0], mx[1], mx[2] + (0*Z_ratio*box_Z_length/2)]) #adjusting the zratio thing shifts the whole boundbox on a diagonal. not so easy. set to 0 for now.
    newregion.center = mx

    newregion.size = Metashape.Vector([box_X_length, box_Y_length, box_Z_length * Z_ratio]) #my way

    chunk.region = newregion
    chunk.updateTransform()

    print ("Bounding box should be aligned now")

update_boundbox()

  
  

