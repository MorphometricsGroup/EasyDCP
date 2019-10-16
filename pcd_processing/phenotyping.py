import imageio
import numpy as np
import open3d as o3d
# from PIL import Image
# from datetime import datetime
from plyfile import PlyData
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import OneClassSVM, SVC
from sklearn.cluster import KMeans


class Classifier(object):
    """
    Variable:
        list path_list
        list kind_list
        set  kind_set
        skln clf
    """

    def __init__(self, path_list, kind_list, core='dtc'):
        """
        :param path_list: the list training png path
            e.g. path_list = ['fore.png', 'back.png']

        :param kind_list: list for related kind for path_list
            -1 is background
             0 is foreground (class 0)
            + 1 is class 1, etc. +

            Example 1: one class with 2 training data
                path_list = ['fore1.png', 'fore2.png']
                kind_list = [0, 0]
            Example 2: two class with 1 training data respectively
                path_list = ['back.png', 'fore.png']
                kind_list = [-1, 0]
            Example 2: multi class with multi training data
                path_list = ['back1.png', 'back2.png', 'leaf1.png', 'leaf2.png', 'flower1.png']
                kind_list = [-1, -1, 0, 0, 1]

        :param core:
            svm: Support Vector Machine Classifier
            dtc: Decision Tree Classifier
        """
        # Check whether correct input
        path_n = len(path_list)
        kind_n = len(kind_list)

        if path_n != kind_n:
            print('Warning: the image number and kind number not matching!')

        self.path_list = path_list[0:min(path_n, kind_n)]
        self.kind_list = kind_list[0:min(path_n, kind_n)]

        # Build Training Array
        self.train_data = np.empty((0, 3))
        self.train_kind = np.empty(0)
        self.build_training_array()

        self.kind_set = set(kind_list)

        if len(self.kind_set) == 1:   # only one class
            self.clf = OneClassSVM()
            # todo: build_svm1class()
        else:  # multi-classes
            if core == 'dtc':
                self.clf = DecisionTreeClassifier(max_depth=20)
                self.clf = self.clf.fit(self.train_data, self.train_kind)
            elif core == 'svm':
                self.clf = SVC()
                # todo: build SVC() classifier

    @staticmethod
    def read_png(file_path):
        img_ndarray = imageio.imread(file_path)
        h, w, d = img_ndarray.shape
        img_2d = img_ndarray.reshape(h * w, d)
        img_np = img_2d[img_2d[:, 3] == 255, 0:3] / 255

        return img_np

    def build_training_array(self):
        for img_path, kind in zip(self.path_list, self.kind_list):
            img_np = self.read_png(img_path)
            kind_np = np.array([kind] * img_np.shape[0])

            self.train_data = np.vstack([self.train_data, img_np])
            self.train_kind = np.hstack([self.train_kind, kind_np])


class Plot(object):

    def __init__(self, ply_path, classifier):
        self.pcd = self.read_ply(ply_path)
        print('[3DPhenotyping] Ply fild loaded')

        self.pcd_xyz = np.asarray(self.pcd.points)
        self.pcd_rgb = np.asarray(self.pcd.colors)

        # get the size of this plot
        self.points_num = self.pcd_xyz.shape[0]

        self.x_max = self.pcd_xyz[:, 0].max()
        self.x_min = self.pcd_xyz[:, 0].min()
        self.x_len = self.x_max - self.x_min

        self.y_max = self.pcd_xyz[:, 1].max()
        self.y_min = self.pcd_xyz[:, 1].min()
        self.y_len = self.y_max - self.y_min

        self.z_max = self.pcd_xyz[:, 2].max()
        self.z_min = self.pcd_xyz[:, 2].min()
        self.z_len = self.z_max - self.z_min

        # classification
        self.pcd_dict = self.classifier_apply(classifier)
        print('[3DPhenotyping] Point clouds classifed')

        # turn to voxel
        self.pcd_voxel, self.voxel_size = self.pcd2voxel()
        self.voxel_num = len(self.pcd_voxel.voxels)
        self.voxel_density = self.points_num / self.voxel_num
        print('[3DPhenotyping] Voxel of splitting 100 part generated')

        self.pcd_cleaned, self.pcd_cleaned_id = self.noise_filter()
        print('[3DPhenotyping] Remove noises in all kinds')

        # start segmentation
        self.plants = self.segmentation()

    @staticmethod
    def read_ply(file_path):
        pcd = o3d.io.read_point_cloud(file_path)
        if not pcd.has_colors():
            cloud_ply = PlyData.read(file_path)
            cloud_data = cloud_ply.elements[0].data
            ply_names = cloud_data.dtype.names

            if 'red' in ply_names:
                colors = np.vstack((cloud_data['red'] / 255, cloud_data['green'] / 255, cloud_data['blue'] / 255)).T
                pcd.colors = o3d.utility.Vector3dVector(colors)
            elif 'diffuse_red' in ply_names:
                colors = np.vstack((cloud_data['diffuse_red'] / 255, cloud_data['diffuse_green'] / 255,
                                    cloud_data['diffuse_blue'] / 255)).T
                pcd.colors = o3d.utility.Vector3dVector(colors)
            else:
                print('Can not find color info in ', ply_names)

        return pcd

    def classifier_apply(self, classifier):
        pcd_xyz_np = np.asarray(self.pcd.points)
        pcd_color_np = np.asarray(self.pcd.colors)

        pred_result = classifier.clf.predict(pcd_color_np)

        pcd_dict = {}

        for k in classifier.kind_set:
            indices = np.where(pred_result == k)[0].tolist()
            pcd_dict[k] = self.pcd.select_down_sample(indices=indices)

        return pcd_dict

    def pcd2voxel(self, part=100):
        # param part: how many part of the shortest axis will be split?
        voxel_size = min(self.x_len, self.y_len, self.z_len) / part
        # convert point cloud to voxel
        pcd_voxel = o3d.geometry.VoxelGrid().create_from_point_cloud(self.pcd, voxel_size=voxel_size)

        return pcd_voxel, voxel_size

    def noise_filter(self):
        pcd_cleaned = {}
        pcd_cleaned_id = {}

        for k in self.pcd_dict.keys():
            if k == -1:   # for background, need to apply statistical outlier removal
                cleaned, indices = self.pcd_dict[-1].remove_statistical_outlier(round(self.voxel_density), 0.01)
                pcd_cleaned[-1], pcd_cleaned_id[-1] = cleaned.remove_radius_outlier(round(self.voxel_density*2),
                                                                                    self.voxel_size)
            else:
                pcd_cleaned[k], pcd_cleaned_id[k] = self.pcd_dict[k].remove_radius_outlier(nb_points=round(self.voxel_density),
                                                                                           radius=self.voxel_size)
        #o3d.visualization.draw_geometries([pcd_cleaned[0]])
        return pcd_cleaned, pcd_cleaned_id

    def write_denoised_ply(self, folder_path):
        for k in self.pcd_dict.keys():
            file_name = folder_path + '_' + str(k) + '.ply'
            o3d.io.write_point_cloud(file_name, self.pcd_cleaned[k])

    def segmentation(self, plant_size=10, plant_num=10):
        # may need user to provide plant size and number for segmentation check
        seg_out = {}
        for k in self.pcd_dict.keys():
            if k == -1:
                continue

            print('[3DPhenotyping][Segmentation] Start segmenting class ' + str(k) + ' Please wait...')
            vect = self.pcd_cleaned[k].cluster_dbscan(eps=self.voxel_size * 10, min_points=round(self.voxel_density),
                                                      print_progress=True)
            vect_np = np.asarray(vect)
            seg_id = np.unique(vect_np)

            print('[3DPhenotyping][Segmentation] class ' + str(k) + ' Segmented')

            pcd_seg_list = []
            pcd_seg_char = np.empty((0, 2))

            for seg in seg_id:
                indices = np.where(vect_np == seg)[0].tolist()
                pcd_seg = self.pcd_cleaned[k].select_down_sample(indices)

                pcd_seg_list.append(pcd_seg)
                char = np.asarray([len(pcd_seg.points), self.calculate_xyz_volumn(pcd_seg)])
                pcd_seg_char = np.vstack([pcd_seg_char, char])

            # cluster by (points number, and volumn) to remove noise segmenation
            km = KMeans(n_clusters=2)
            km.fit(pcd_seg_char)

            class0 = pcd_seg_char[km.labels_ == 0, :]
            class1 = pcd_seg_char[km.labels_ == 1, :]

            # find the class label with largest point clouds (plants)
            if class0.mean(axis=0)[0] > class1.mean(axis=0)[0]:
                plant_id = np.where(km.labels_ == 0)[0].tolist()
            else:
                plant_id = np.where(km.labels_ == 1)[0].tolist()

            seg_out[k] = [Plant(pcd_seg_list[i], kind=k) for i in plant_id]

        return seg_out


    @staticmethod
    def calculate_xyz_volumn(pcd):
        pcd_xyz = np.asarray(pcd.points)

        x_len = pcd_xyz[:, 0].max() - pcd_xyz[:, 0].min()
        y_len = pcd_xyz[:, 1].max() - pcd_xyz[:, 1].min()
        z_len = pcd_xyz[:, 2].max() - pcd_xyz[:, 2].min()

        return x_len * y_len * z_len


    #temp func
    def show_seged_plants(self):
        show_list = []

        for seg in self.plants[0]:
            seg.pcd.paint_uniform_color(np.random.rand(3).tolist())
            show_list.append(seg.pcd)

        o3d.visualization.draw_geometries(show_list)


class Plant(object):

    def __init__(self, pcd, kind):
        self.pcd = pcd
        self.kind = kind


if __name__ == '__main__':
    # >>> from phenotyping import *

    # testing examples, and show how to use the APIs
    cla = Classifier(path_list=['../example/training_data/fore_rm_y.png',
                                '../example/training_data/back.png'],
                     kind_list=[0, -1], core='dtc')
    # can write for loops here for batch processing for a ply list
    plot1 = Plot('../example/S06.ply', cla)   # size in meter
    # save ply if necessary
    #plot1.write_denoised_ply('./')
    print(plot1.plants)
    plot1.show_seged_plants()