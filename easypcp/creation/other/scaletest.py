import os, Metashape

doc = Metashape.Document()
scalebar_data = list()

doc.open('T:/2020agisoft/191227pheno/canon-sp1-group1-1/canon-sp1-group1-1-v047-all-nocross-high.psx')
chunk = doc.chunk
#chunk.addScalebar('target 23','target 24')

for marker in chunk.markers:
    if (marker.label == 'target 23'):
        scale1_1 = marker
    elif (marker.label == 'target 24'):
        scale1_2 = marker
    elif (marker.label == 'target 31'):
        scale2_1 = marker
    elif (marker.label == 'target 32'):
        scale2_2 = marker
    elif (marker.label == 'target 71'):
        scale3_1 = marker
    elif (marker.label == 'target 72'):
        scale3_2 = marker
        

chunk.addScalebar(scale1_1,scale1_2)
chunk.addScalebar(scale2_1,scale2_2)
chunk.addScalebar(scale3_1,scale3_2)

for scalebar in chunk.scalebars:
    print(scalebar.label, scalebar.reference.distance)
    #print(scalebar.label, float(scalebar.reference.distance))