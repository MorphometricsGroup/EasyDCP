import os
import colorsys
import imageio
import shutil
import time
import numpy as np
import open3d as o3d
import pandas as pd
from copy import copy
from scipy.spatial import ConvexHull
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import OneClassSVM, SVC
from sklearn.cluster import KMeans
from skimage.measure import regionprops

import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
from scipy.stats import gaussian_kde

from pcd_tools import merge_pcd, read_ply, pcd2binary
from geometry.min_bounding_rect import min_bounding_rect
from geometry.fit_ellipse import *


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
        self.pcd = read_ply(ply_path)
        print('[3DPhenotyping] Ply file "' + self.ply_path + '" loaded')
        self._get_temp_root()

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

        self.traits = self._get_traits()

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
                char = np.asarray([len(pcd_seg.points) ** 0.5, self.calculate_xyz_volumn(pcd_seg)])
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
            # generate distinguishable random colors
            num = len(pcd_list)
            dist_colors = []
            i = 0
            step = 360.0 / num
            while i < 360:
                h = i
                s = 90 + np.random.rand() * 10
                l = 50 + np.random.rand() * 10
                r, g, b = colorsys.hls_to_rgb(h/360.0, l/ 100.0, s/ 100.0)
                dist_colors.append((r, g, b))
                i += step
            # apply colors
            for i, pcd in enumerate(pcd_list):
                pcd_copy = copy(pcd)
                pcd_copy.paint_uniform_color(dist_colors[i])
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

    def _get_traits(self):
        out_dict = {'Plot': [], 'kind': [], 'center.x(m)': [], 'center.y(m)': [],
                    'min_rect_width(m)':[], 'min_rect_length(m)':[], 'hover_area(m2)':[], 'PLA(cm2)':[],
                    'centroid.x(m)':[], 'centroid.y(m)':[], 'long_axis(m)':[], 'short_axis(m)':[], 'orient_deg2xaxis':[],
                    'height(m)':[], 'convex_volume(m3)':[], 'voxel_volume(m3)':[]}
        folder, tail = os.path.split(os.path.abspath(self.ply_path))

        for k in self.plants.keys():
            for i, plant in enumerate(self.plants[k]):
                out_dict['Plot'].append(tail[:-4])
                out_dict['kind'].append(plant.kind)
                out_dict['center.x(m)'].append(plant.center[0])
                out_dict['center.y(m)'].append(plant.center[1])
                out_dict['min_rect_width(m)'].append(plant.width)
                out_dict['min_rect_length(m)'].append(plant.length)
                out_dict['hover_area(m2)'].append(plant.hull_area)
                out_dict['PLA(cm2)'].append(plant.pla)
                out_dict['centroid.x(m)'].append(plant.centroid[0])
                out_dict['centroid.y(m)'].append(plant.centroid[1])
                out_dict['long_axis(m)'].append(plant.major_axis)
                out_dict['short_axis(m)'].append(plant.minor_axis)
                out_dict['orient_deg2xaxis'].append(plant.orient_degree)
                out_dict['height(m)'].append(plant.height)
                out_dict['convex_volume(m3)'].append(plant.volume_hull_ground)
                out_dict['voxel_volume(m3)'].append(plant.volumn_voxel)

        df_out = pd.DataFrame(out_dict)
        df_out = df_out.sort_values(by=['center.x(m)', 'center.y(m)']).reset_index()
        df_out['Plant_id'] = df_out.index.values + 1
        df_out = df_out[['Plot', 'Plant_id', 'kind', 'center.x(m)', 'center.y(m)',
                         'min_rect_width(m)', 'min_rect_length(m)', 'hover_area(m2)', 'PLA(cm2)',
                         'centroid.x(m)', 'centroid.y(m)', 'long_axis(m)', 'short_axis(m)', 'orient_deg2xaxis',
                         'height(m)', 'convex_volume(m3)', 'voxel_volume(m3)', 'index']]

        return df_out

    def _get_temp_root(self):
        folder, tail = os.path.split(os.path.abspath(self.ply_path))
        ply_name = tail[:-4]
        self.temp_root = os.path.join(folder, ply_name)
        if os.path.exists(self.temp_root):
            shutil.rmtree(self.temp_root)
        time.sleep(1)   # ensure the folder is cleared
        os.mkdir(self.temp_root)

    def write_ply(self):
        for k in self.pcd_dict.keys():
            o3d.io.write_point_cloud(os.path.join(self.temp_root, 'class[' + str(k) + '].ply'), self.pcd_dict[k])
            o3d.io.write_point_cloud(os.path.join(self.temp_root, 'class[' + str(k) + ']-rm_noise.ply'), self.pcd_cleaned[k])
            if k > -1:
                for i, plant in enumerate(self.plants[k]):
                    index_show = self.traits[self.traits['index'] == i]['Plant_id'].values[0]
                    file_name = 'class[' + str(k) + ']-plant' + str(index_show) + '.ply'
                    file_path = os.path.join(self.temp_root, file_name)
                    print('[3DPhenotyping][Output] writing file "'+ file_path + '"')
                    o3d.io.write_point_cloud(file_path, plant.pcd)

        print('[3DPhenotyping][Output] All ply file exported')

    def write_fig(self):
        print('[3DPhenotyping][Output] writing traits figures')
        for i, raw_id in enumerate(list(self.traits['index'])):
            print('[3DPhenotyping][Output][Plant ' + str(i+1) + '] traits preparation')
            fig, ax = plt.subplots(1, 3, figsize=(10, 3), dpi=300,
                                   gridspec_kw={'width_ratios': [3, 3, 1]})
            plant = self.plants[0][raw_id]
            pcd = plant.pcd
            pcd_xyz = np.asarray(pcd.points)

            x = pcd_xyz[:, 0]
            y = pcd_xyz[:, 1]
            z = pcd_xyz[:, 2]

            convex_hull = np.vstack([plant.plane_hull, plant.plane_hull[0, :]])

            corner = plant.rect_res[5]
            rect_corner = np.vstack([corner, corner[0, :]])

            x0 = plant.centroid[0]
            y0 = plant.centroid[1]
            phi = plant.orient_degree

            maj_x = np.cos(np.deg2rad(phi)) * 0.5 * plant.major_axis
            maj_y = np.sin(np.deg2rad(phi)) * 0.5 * plant.major_axis
            min_x = np.sin(np.deg2rad(phi)) * 0.5 * plant.minor_axis
            min_y = np.cos(np.deg2rad(phi)) * 0.5 * plant.minor_axis

            z_lin = np.linspace(z.min(), z.max(), 1000)
            kernel = gaussian_kde(z)
            y_d = kernel(z_lin)

            ell = Ellipse(plant.centroid, plant.major_axis, plant.minor_axis, phi, alpha=0.5, zorder=2)

            print('[3DPhenotyping][Output][Plant ' + str(i + 1) + '] Plotting')
            ax[0].scatter(x, y, marker='.', color='C2', alpha=0.2, zorder=0)
            ax[0].add_artist(ell)
            ax[0].plot((x0 - maj_x, x0 + maj_x), (y0 - maj_y, y0 + maj_y), '-k', linewidth=2.5)
            ax[0].plot((x0 + min_x, x0 - min_x), (y0 - min_y, y0 + min_y), '-k', linewidth=2.5)
            ax[0].plot(convex_hull[:, 0], convex_hull[:, 1], 'C0--', alpha=0.5, zorder=5)
            ax[0].scatter(convex_hull[:, 0], convex_hull[:, 1], marker='.', color='C3', zorder=10)
            ax[0].plot(rect_corner[:, 0], rect_corner[:, 1], color='C1', alpha=0.5, zorder=15)
            ax[0].plot(x0, y0, 'r.', zorder=20)

            ax[0].axis('scaled')
            ax[0].set_xlabel('X')
            ax[0].set_ylabel('Y', rotation=0)

            ax[1].scatter(x, z, marker='.', color='C2')
            ax[1].set_xlabel('X')
            ax[1].set_ylabel('Z', rotation=0)

            ax[1].set_title('Plant' + str(i+1))

            ax[2].plot(y_d, z_lin)
            ax[2].set_xlabel('Histgram')
            ax[2].set_yticklabels('')
            ax[2].plot([0, y_d.max()], [np.percentile(z, 90), np.percentile(z, 90)])
            print('[3DPhenotyping][Output][Plant ' + str(i + 1) + '] Plotting finished')

            plt.tight_layout()
            plt.savefig(os.path.join(self.temp_root, 'plant' + str(i+1) + '.jpg'))
            plt.close()


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

        self.centroid, self.major_axis, self.minor_axis, self.orient_degree = self.fit_region_props()
        self.rect_res = min_bounding_rect(self.plane_hull)
        # rect_res = (rot_angle, area, width, length, center_point, corner_points)
        self.width = self.rect_res[2]   # unit is m
        self.length = self.rect_res[3]   # unit is m

        self.pla = self.calcu_projected_leaf_area()

        self.hull_boundary = self.build_cut_boundary()
        self.pcd_ground = self.hull_boundary.crop_point_cloud(self.plot.pcd_cleaned[-1])

        self.pcd_merged = merge_pcd([self.pcd, self.pcd_ground])
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

    def fit_region_props(self):
        binary, px_num_per_cm, corner = pcd2binary(self.pcd)
        x_min, y_min = corner
        regions = regionprops(binary, coordinates='xy')
        props = regions[0]          # this is all coordinate in converted binary images

        # convert coordinate from binary images to real point cloud
        y0, x0 = props.centroid
        center = ( x0 / px_num_per_cm / 100 + x_min, y0 / px_num_per_cm /100 + y_min)

        major_axis = props.major_axis_length / px_num_per_cm / 100
        minor_axis = props.minor_axis_length / px_num_per_cm / 100

        phi = props.orientation
        angle = - phi * 180 / np.pi # included angle with x axis, clockwise, by regionprops default

        self.pla_img = binary  # preojected leaf area
        self.px_num_per_cm = px_num_per_cm

        return center, major_axis, minor_axis, angle

    def calcu_projected_leaf_area(self):
        kind, number = np.unique(self.pla_img, return_counts=True)
        back_num = number[0]
        fore_num = number[1]

        pixel_size = (1 / self.px_num_per_cm) ** 2   # unit is cm2

        return fore_num * pixel_size

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

    def pcd2voxel(self, part=50):
        # param part: how many part of the shortest axis will be split?
        voxel_size = min(self.x_len, self.y_len, self.z_len) / part
        # convert point cloud to voxel
        pcd_voxel = o3d.geometry.VoxelGrid().create_from_point_cloud(self.pcd, voxel_size=voxel_size)
        return pcd_voxel, voxel_size