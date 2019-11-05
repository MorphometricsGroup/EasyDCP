from phenotyping import *

cla = Classifier(path_list=['../example/training_data/fore_rm_y.png',
                            '../example/training_data/back.png'],
                 kind_list=[0, -1], core='dtc')

plot1 = Plot('../example/S18.debug.ply', cla, show_steps=True)   # size in meter
# save ply if necessary
plot1.write_ply()
plot1_df = plot1.get_traits()
print(plot1_df)
plot1_df.to_csv('plot1.csv')