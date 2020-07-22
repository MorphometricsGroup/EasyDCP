import __init__
import phenotypy as pnt
import pandas as pd

cla = pnt.Classifier(path_list=['data/brocoli_train_plant1.ply',
                                'data/brocoli_train_soil.ply',
                                'data/brocoli_train_soil_gcp.ply'],
                     kind_list=[0, -1, -1], core='dtc')
plot = pnt.Plot('data/brocoli.ply', cla, output_path='output')
#seg = plot.auto_segmentation()
seg = plot.dbscan_segment(eps=1, min_points=10)
print(seg)
#df = plot.get_traits()

#print(df)
