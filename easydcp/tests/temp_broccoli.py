import __init__
import easypcp as pcp
import pandas as pd

cla = pcp.Classifier(path_list=['data/brocoli_train_plant1.ply',
                                'data/brocoli_train_soil.ply',
                                'data/brocoli_train_soil_gcp.ply'],
                     kind_list=[0, -1, -1], core='dtc')
plot = pcp.Plot('data/brocoli.ply', cla, output_path='output')
#seg = plot.auto_segmentation()
seg = plot.dbscan_segment(eps=1, min_points=10)
print(seg)
#df = plot.get_traits()

#print(df)
