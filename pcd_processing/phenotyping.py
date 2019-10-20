import os
import imageio
import shutil
import time
import numpy as np
import open3d as o3d
import pandas as pd
# from PIL import Image
# from datetime import datetime
from copy import copy
from plyfile import PlyData
from scipy.spatial import ConvexHull
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import OneClassSVM, SVC
from sklearn.cluster import KMeans
from min_bounding_rect import min_bounding_rect


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
        print('[3DPhenotyping][Classifier] Start building classifier')
        path_n = len(path_list)
        kind_n = len(kind_list)

        if path_n != kind_n:
            print('[3DPhenotyping][Classifier][Warning] the image number and kind number not matching!')

        self.path_list = path_list[0:min(path_n, kind_n)]
        self.kind_list = kind_list[0:min(path_n, kind_n)]

        # Build Training Array
        self.train_data = np.empty((0, 3))
        self.train_kind = np.empty(0)
        self.build_training_array()
        print('[3DPhenotyping][Classifier] Training data prepared')

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
        print('[3DPhenotyping][Classifier] Classifying model built')

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
    """
    =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    | The vector information are not loaded currently |
    =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    Variables:
        pcd -> open3d.geometry.pointclouds object

        pcd_xyz = np.asarray(pcd.points) -> numpy.array nx3 object

        pcd_rgb = np.asarray(pcd.colors) -> numpy.array nx3 object

        x_max, y_min, z_len: # coordinate information for point clouds

        pcd_dict -> dict
            {'-1': o3d.geometry.pointclouds, # background
              '0': o3d.geometry.pointclouds, # foreground
              '1': o3d.geometry.pointclouds, # (optional) foreground 2
              ...etc.}

        pcd_cleaned -> same as pcd_dict

        plants -> dict
            {'0': [Plant, Plant, Plant, ...],  # background -1 not included
             '1': [Plant, Plant, Plant, ...].  # (optional)
             ... etc. }
    """

    def __init__(self, ply_path, classifier, show_steps=False):
        """
        :param ply_path:
        :param classifier:
        :param show_steps: if open this, the progress won't continue until the visualizing window is turned off
        """
        self.ply_path = ply_path
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
        if show_steps:
            self._show_pcd(list(self.pcd_dict.values()), window_name='classified', color='Rand')

        # turn to voxel
        self.pcd_voxel, self.voxel_size = self.pcd2voxel()
        self.voxel_num = len(self.pcd_voxel.voxels)
        self.voxel_density = self.points_num / self.voxel_num

        # remove noises
        self.pcd_cleaned, self.pcd_cleaned_id = self.noise_filter()

        if show_steps:
            self._show_pcd(list(self.pcd_cleaned.values()), window_name='rm_noised', color='Rand')

        # start segmentation
        self.plants = self.segmentation()
        if show_steps:
            show_list = [copy(plant.pcd) for plant in self.plants[0]]
            self._show_pcd(show_list, window_name='Plants', color='Rand')

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
        print('[3DPhenotyping][Classify] Start Classifying')
        pred_result = classifier.clf.predict(self.pcd_rgb)

        pcd_dict = {}

        for k in classifier.kind_set:
            print('[3DPhenotyping][Classify] Begin for class ' + str(k))
            indices = np.where(pred_result == k)[0].tolist()
            pcd_dict[k] = self.pcd.select_down_sample(indices=indices)
            print('[3DPhenotyping][Classify] kind ' + str(k) + ' classified')

        return pcd_dict

    def pcd2voxel(self, part=100):
        # param part: how many part of the shortest axis will be split?
        print('[3DPhenotyping][Voxel] Start Voxel of splitting')
        voxel_size = min(self.x_len, self.y_len, self.z_len) / part
        # convert point cloud to voxel
        pcd_voxel = o3d.geometry.VoxelGrid().create_from_point_cloud(self.pcd, voxel_size=voxel_size)

        print('[3DPhenotyping][Voxel] Voxel of splitting 100 part generated')
        return pcd_voxel, voxel_size

    def noise_filter(self):
        pcd_cleaned = {}
        pcd_cleaned_id = {}
        print('[3DPhenotyping][rm_noise] Remove noises')
        for k in self.pcd_dict.keys():
            if k == -1:   # for background, need to apply statistical outlier removal
                cleaned, indices = self.pcd_dict[-1].remove_statistical_outlier\
                    (nb_neighbors=round(self.voxel_density), std_ratio=0.01)
                pcd_cleaned[-1], pcd_cleaned_id[-1] = cleaned.remove_radius_outlier\
                    (nb_points=round(self.voxel_density*2), radius=self.voxel_size)
            else:
                pcd_cleaned[k], pcd_cleaned_id[k] = self.pcd_dict[k].remove_radius_outlier\
                    (nb_points=round(self.voxel_density), radius=self.voxel_size)
            print('[3DPhenotyping][rm_noise] kind ' + str(k) + ' noise removed')

        return pcd_cleaned, pcd_cleaned_id

    def segmentation(self):   # plant_size=10, plant_num=10
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

            # KMeans to find the class of noise and plants
            # # Data prepare for clustering
            pcd_seg_list = []
            pcd_seg_char = np.empty((0, 2))

            for seg in seg_id:
                indices = np.where(vect_np == seg)[0].tolist()
                pcd_seg = self.pcd_cleaned[k].select_down_sample(indices)

                pcd_seg_list.append(pcd_seg)
                char = np.asarray([len(pcd_seg.points), self.calculate_xyz_volumn(pcd_seg)])
                pcd_seg_char = np.vstack([pcd_seg_char, char])

            print('[3DPhenotyping][Segmentation][Clustering] class ' + str(k) + ' Cluster Data Prepared')

            # # cluster by (points number, and volumn) to remove noise segmenation
            km = KMeans(n_clusters=2)
            km.fit(pcd_seg_char)

            class0 = pcd_seg_char[km.labels_ == 0, :]
            class1 = pcd_seg_char[km.labels_ == 1, :]

            # find the class label with largest point clouds (plants)
            if class0.mean(axis=0)[0] > class1.mean(axis=0)[0]:
                plant_id = np.where(km.labels_ == 0)[0].tolist()
            else:
                plant_id = np.where(km.labels_ == 1)[0].tolist()

            seg_out[k] = [Plant(self, pcd_seg_list[p], i+1, kind=k) for i, p in enumerate(plant_id)]

            print('[3DPhenotyping][Segmentation][Clustering] class ' + str(k) + ' Clustered')

        return seg_out

    @staticmethod
    def calculate_xyz_volumn(pcd):
        pcd_xyz = np.asarray(pcd.points)

        x_len = pcd_xyz[:, 0].max() - pcd_xyz[:, 0].min()
        y_len = pcd_xyz[:, 1].max() - pcd_xyz[:, 1].min()
        z_len = pcd_xyz[:, 2].max() - pcd_xyz[:, 2].min()

        return x_len * y_len * z_len

    @staticmethod
    def _show_pcd(pcd_list, window_name='Open3D', color=None):
        # color =
        #   None:  to display original color
        #   'Rand': to display a rand color
        #   [(0, 0.5, 1), ...]   max 1 for 255 color
        if isinstance(color, str):
            show_list = []
            for pcd in pcd_list:
                pcd_copy = copy(pcd)
                pcd_copy.paint_uniform_color(np.random.rand(3).tolist())
                show_list.append(pcd_copy)
        elif isinstance(color, list):
            show_list = []
            for i, c_tuple in enumerate(color):
                pcd_copy = copy(pcd_list[i])
                pcd_copy.paint_uniform_color(c_tuple)
                show_list.append(pcd_copy)
        else:   # color is None:
            show_list = pcd_list

        print('[3DPhenotyping][Visualizing] Visualizing, calculation paused')
        o3d.visualization.draw_geometries(show_list, window_name=window_name)

    def write_ply(self):
        folder, tail = os.path.split(os.path.abspath(self.ply_path))
        ply_name = tail[:-4]
        temp_root = os.path.join(folder, ply_name)

        if os.path.exists(temp_root):
            shutil.rmtree(temp_root)
        time.sleep(0.2)   # ensure the folder is cleared
        os.mkdir(temp_root)

        for k in self.pcd_dict.keys():
            o3d.io.write_point_cloud(os.path.join(temp_root, 'class[' + str(k) + '].ply'), self.pcd_dict[k])
            o3d.io.write_point_cloud(os.path.join(temp_root, 'class[' + str(k) + ']-rm_noise.ply'), self.pcd_cleaned[k])
            if k > -1:
                for i, plant in enumerate(self.plants[k]):
                    o3d.io.write_point_cloud(os.path.join(temp_root, 'class[' + str(k) + ']-plant' + str(i) + '.ply'),
                                             plant.pcd)

        print('[3DPhenotyping][Output] All ply file exported')

    def get_traits(self):
        out_dict = {'Plot': [], 'kind': [], 'x(m)': [], 'y(m)': [],
                    'width(m)':[], 'length(m)':[], 'hover_area(m2)':[],
                    'height(m)':[], 'convex_volume(m3)':[], 'voxel_volume(m3)':[]}
        folder, tail = os.path.split(os.path.abspath(self.ply_path))

        for k in self.plants.keys():
            for i, plant in enumerate(self.plants[k]):
                out_dict['Plot'].append(tail[:-4])
                out_dict['kind'].append(plant.kind)
                out_dict['x(m)'].append(plant.center[0])
                out_dict['y(m)'].append(plant.center[1])
                out_dict['width(m)'].append(plant.width)
                out_dict['length(m)'].append(plant.length)
                out_dict['hover_area(m2)'].append(plant.hull_area)
                out_dict['height(m)'].append(plant.height)
                out_dict['convex_volume(m3)'].append(plant.volume_hull_ground)
                out_dict['voxel_volume(m3)'].append(plant.volumn_voxel)

        df_out = pd.DataFrame(out_dict)
        df_out = df_out.sort_values(by=['x(m)', 'y(m)']).reset_index()
        df_out['Plant_id'] = df_out.index.values + 1
        df_out = df_out[['Plot', 'Plant_id', 'kind', 'x(m)', 'y(m)',
                         'width(m)', 'length(m)', 'hover_area(m2)', 'height(m)',
                         'convex_volume(m3)', 'voxel_volume(m3)']]

        return df_out

class Plant(object):

    def __init__(self, parent, pcd, indices, kind):
        self.plot = parent
        self.pcd = pcd
        self.indices = '[Plant ' + str(indices) + ']'
        self.kind = kind
        self.center = pcd.get_center()

        print('[3DPhenotyping][Traits]' +self.indices + 'Calculating start.')

        self.pcd_xyz = np.asarray(self.pcd.points)
        self.pcd_rgb = np.asarray(self.pcd.colors)

        self.x_max = self.pcd_xyz[:, 0].max()
        self.x_min = self.pcd_xyz[:, 0].min()
        self.x_len = self.x_max - self.x_min

        self.y_max = self.pcd_xyz[:, 1].max()
        self.y_min = self.pcd_xyz[:, 1].min()
        self.y_len = self.y_max - self.y_min

        self.z_max = self.pcd_xyz[:, 2].max()
        self.z_min = self.pcd_xyz[:, 2].min()
        self.z_len = self.z_max - self.z_min

        self.plane_hull, self.hull_area = self.plane_convex_hull_calc()  # vertex_set (2D ndarray), m^2
        print('[3DPhenotyping][Traits]' + self.indices + ' 2D convex hull generated')

        res = min_bounding_rect(self.plane_hull)
        # res = (rot_angle, area, width, length, center_point, corner_points)
        self.width = res[2]   # unit is m
        self.length = res[3]   # unit is m

        self.hull_boundary = self.build_cut_boundary()
        self.pcd_ground = self.hull_boundary.crop_point_cloud(self.plot.pcd_cleaned[-1])

        self.pcd_merged = self.merge_pcd([self.pcd, self.pcd_ground])
        print('[3DPhenotyping][Traits]' + self.indices + ' ground points merged.')

        # calculate stereo convex hull
        convex_hull_merged = self.pcd_merged.compute_convex_hull()
        self.stereo_hull_merged = np.asarray(convex_hull_merged.vertices)
        self.height = self.stereo_hull_merged[:,2].max() - self.stereo_hull_merged[:,2].min()

        convex_hull_merged_scipy = ConvexHull(self.stereo_hull_merged)
        self.volume_hull_ground = convex_hull_merged_scipy.volume
        print('[3DPhenotyping][Traits]' + self.indices + ' 3D convex hull calculating finished.')

        # todo: save convex hull to ply
        # o3d.io.write_triangle_mesh('hull.ply', convex_hull)

        # voxel volume
        self.pcd_voxel, self.voxex_size = self.pcd2voxel()
        self.voxel_num = len(self.pcd_voxel.voxels)
        self.volumn_voxel = self.voxel_num * (self.voxex_size) ** 3 # unit is m3
        print('[3DPhenotyping][Traits]' + self.indices + ' voxel generation finished.')

    def plane_convex_hull_calc(self):
        xy = self.pcd_xyz[:, 0:2]
        hull = ConvexHull(xy)
        hull_xy = xy[hull.vertices, :]
        # in scipy, 2D hull.area is perimeter, hull.volume is area
        # https://stackoverflow.com/questions/35664675/in-scipys-convexhull-what-does-area-measure
        #
        # >>> points = np.array([[-1,-1], [1,1], [-1, 1], [1,-1]])
        # >>> hull = ConvexHull(points)
        # ==== 2D ====
        # >>> print(hull.volume)
        # 4.00
        # >>> print(hull.area)
        # 8.00
        # ==== 3D ====
        # >>> points = np.array([[-1,-1, -1], [-1,-1, 1],
        # ...                    [-1, 1, -1], [-1, 1, 1],
        # ...                    [1, -1, -1], [1, -1, 1],
        # ...                    [1,  1, -1], [1,  1, 1]])
        # >>> hull = ConvexHull(points)
        # >>> hull.area
        # 24.0
        # >>> hull.volume
        # 8.0
        return hull_xy, hull.volume

    def build_cut_boundary(self):
        z_coord = np.zeros((self.plane_hull.shape[0], 1))
        polygon = np.hstack([self.plane_hull, z_coord])
        polygon = np.vstack([polygon, polygon[0, :]])

        boundary = o3d.visualization.SelectionPolygonVolume()
        boundary.orthogonal_axis = "Z"
        boundary.bounding_polygon = o3d.utility.Vector3dVector(polygon)
        boundary.axis_max = self.plot.z_max
        boundary.axis_min = self.plot.z_min

        return boundary

    @staticmethod
    def merge_pcd(pcd_list):
        final_pcd = o3d.geometry.PointCloud()
        xyz = np.empty((0, 3))
        rgb = np.empty((0, 3))

        for pcd in pcd_list:
            pcd_xyz = np.asarray(pcd.points)
            pcd_rgb = np.asarray(pcd.colors)

            xyz = np.vstack([xyz, pcd_xyz])
            rgb = np.vstack([rgb, pcd_rgb])

        final_pcd.points = o3d.utility.Vector3dVector(xyz)
        final_pcd.colors = o3d.utility.Vector3dVector(rgb)

        return final_pcd

    def pcd2voxel(self, part=50):
        # param part: how many part of the shortest axis will be split?
        voxel_size = min(self.x_len, self.y_len, self.z_len) / part
        # convert point cloud to voxel
        pcd_voxel = o3d.geometry.VoxelGrid().create_from_point_cloud(self.pcd, voxel_size=voxel_size)
        return pcd_voxel, voxel_size



if __name__ == '__main__':
    # >>> from phenotyping import *

    # testing examples, and show how to use the APIs
    # build the general classifier first, to avoid rebuild every time for each ply file.
    cla = Classifier(path_list=['../example/training_data/fore_rm_y.png',
                                '../example/training_data/back.png'],
                     kind_list=[0, -1], core='dtc')

    # for single ply file
    plot1 = Plot('../example/S01.ply', cla)#, show_steps=True)   # size in meter
    # save ply if necessary
    plot1.write_ply()
    plot1_df = plot1.get_traits()
    print(plot1_df)
    plot1_df.to_csv('plot1.csv')

    # batch processing
    plot_set = ['../example/S02.ply', '../example/S03.ply']
    # change to empty list for batch processing
    # >>> result_container = []
    result_container = [plot1_df]
    # here is just for reuse S01 for testing

    for plot in plot_set:
        # show_steps=True to display output among calculation to check correct or not
        plot_class = Plot(plot, cla, show_steps=False)
        # if need to save points among calculation for checking or other software
        plot_class.write_ply()
        plot_df = plot_class.get_traits()
        result_container.append(plot_df)

    plot_all = pd.concat(result_container, axis=0).reset_index()
    plot_all.to_csv('plot_outputs.csv', index=False)