from phenotyping import *

cla = Classifier(path_list=['../example/training_data/fore_rm_y.png',
                            '../example/training_data/back.png'],
                 kind_list=[0, -1], core='dtc')

plot1 = Plot('../example/S01.ply', cla, show_steps=True)   # size in meter
# save ply if necessary
plot1.write_ply()
print(plot1.traits)
plot1.traits.to_csv('plot1.csv')