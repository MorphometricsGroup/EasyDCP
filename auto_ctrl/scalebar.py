# script for automatically creating and importing scalebars from a csv file.
# modified from script by Alexey Pasumansky and http://hairystickman.co.uk/photoscan-scale-bars/
# by Alex Feldman - UTokyo Field Phenomics Lab

# updated 2019.6.4
# compatibility Metashape Pro 1.5.2

import Metashape
from PySide2 import QtCore, QtGui

doc = Metashape.app.document
chunk = doc.chunk
print("Create and import scalebars")

msg = "Choose a scalebar csv file"

path = Metashape.app.getOpenFileName("Select input text file:")
print ('@#$#@  ',path)
file = open(path, "rt")

eof = False
line = file.readline()

chunk.detectMarkers(tolerance=100)

while not eof:
 #split the line and load into variables
 point1, point2, dist, acc = line.split(",")

 #iterate through chunk markers and see if there is a match for point 1
 if (len(chunk.markers) > 0):
	 for marker in chunk.markers:
		 if (marker.label == point1):
			 scale1 = marker
			 #iterate through chunk markers and see if there is a match for point 2
			 for marker in chunk.markers:
				 if (marker.label == point2):
					 scale2 = marker

					 #create a new scale bar between points if they exist and set distance
					 scalebar = chunk.addScalebar(scale1,scale2)
					 scalebar.reference.distance = float(dist)
					 nopair = 0
				 else:
					 nopair = 1
		 else:
			 nopair = 0
		 
	 if nopair:
		 print("Missing one or other end of point")

 else:
	 print("no markers")

 print (len(line), line)
 #reading the next line in input file
 line = file.readline()
 print (">",len(line), line)
 if len(line) == 0:
	 eof = True
	 print (eof)
 else:
	 print ("x",eof)
 #break

file.close()
Metashape.app.update()
print("Script finished")