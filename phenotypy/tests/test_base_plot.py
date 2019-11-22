import __init__
import pytest
import phenotypy as pnt
import pandas as pd

@pytest.fixture(scope="session", autouse=True)
def plot_init():
    cla = pnt.Classifier(path_list=['data/weed_fore.png',
                                    'data/weed_back.png'],
                         kind_list=[0, -1], core='dtc')

    plot = pnt.Plot('data/weed.ply', cla, output_path='output')
    return plot

def test_plot_auto_segmentation(plot_init):
    seg = plot_init.auto_segmentation()
    print(type(seg), len(seg))
    for k in seg.keys():
        print(k, len(seg[k]))

def test_plot_output(plot_init):
    seg = plot_init.auto_segmentation()
    df = plot_init.get_traits(seg, 0.06)
    print(df)
    print(list(df.columns))


'''
class TestMain(unittest.TestCase):

    def setUp(self):
        print('start')
        self.cla = pnt.Classifier(path_list=['data/weed_fore.png',
                                             'data/weed_back.png'],
                              kind_list=[0, -1], core='dtc')

    def tearDown(self):
        print("end")

    def test_plot_init(self):
        plot = pnt.Plot('data/weed.ply', self.cla, output_path='output')
        seg = plot.auto_segmentation()
        print(seg)

    def test0_one_processing(self):
        plot = pnt.Plot('data/weed.ply', self.cla, show_steps=False)
        print(plot.traits)
        plot.write_ply(savepath='output')
        plot.write_fig(savepath='output')
        plot.traits.to_csv('output/weed.csv')


    def test1_batch_processing(self):
        plot_set = ['data/weed.ply', 'data/weed.ply']
        result_container = []

        for plot in plot_set:
            # show_steps=True to display output among calculation to check correct or not
            plot_class = pnt.Plot(plot, self.cla, show_steps=False)
            result_container.append(plot_class.traits)

        plot_all = pd.concat(result_container, axis=0).reset_index()
        plot_all.to_csv('output/weed_batch.csv', index=False)
    

class TestPotato(unittest.TestCase):

    def setUp(self):
        print('start')
        self.cla = pnt.Classifier(path_list=['data/potato_fore.png',
                                             'data/potato_back.png'],
                              kind_list=[0, -1], core='dtc')

    def test0_one_processing(self):
        plot = pnt.Plot('data/potato.ply', self.cla, show_steps=False)
        print(plot.traits)
        plot.write_ply(savepath='output')
        plot.write_fig(savepath='output')
        plot.traits.to_csv('output/potato.csv')
    '''

if __name__ == '__main__':
    pytest.main()
