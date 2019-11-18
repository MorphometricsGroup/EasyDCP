import unittest
from phenotypy.base import *

class TestMain(unittest.TestCase):

    def setUp(self):
        print('start')
        self.cla = Classifier(path_list=['../example/training_data/fore_rm_y.png',
                                    '../example/training_data/back.png'],
                              kind_list=[0, -1], core='dtc')

    def tearDown(self):
        print("end")

    def test0_one_processing(self):
        plot = Plot('../example/S01.ply', self.cla, show_steps=False)
        print(plot.traits)
        plot.write_ply()
        plot.write_fig()
        plot.traits.to_csv('plot.csv')

    def test1_batch_processing(self):
        plot_set = ['../example/S02.ply', '../example/S03.ply']
        result_container = []

        for plot in plot_set:
            # show_steps=True to display output among calculation to check correct or not
            plot_class = Plot(plot, self.cla, show_steps=False)
            # if need to save points among calculation for checking or other software
            plot_class.write_ply()
            plot_class.write_fig()
            result_container.append(plot_class.traits)

        plot_all = pd.concat(result_container, axis=0).reset_index()
        plot_all.to_csv('plot_outputs.csv', index=False)

if __name__ == '__main__':
    unittest.main()
