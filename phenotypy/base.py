import os
import imageio
import numpy as np
import open3d as o3d
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import OneClassSVM, SVC
from sklearn.cluster import KMeans
from skimage.measure import regionprops

from phenotypy.pcd_tools import (merge_pcd,
                                 pcd2binary,
                                 pcd2voxel,
                                 calculate_xyz_volume,
                                 convex_hull2d,
                                 build_cut_boundary)
from phenotypy.geometry.min_bounding_rect import min_bounding_rect
from phenotypy.io.folder import make_dir
from phenotypy.io.pcd import read_ply
from phenotypy.plotting.stereo import show_pcd


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

    def predict(self, vars):
        return self.clf.predict(vars)


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

        pcd_classified -> dict
            {'-1': o3d.geometry.pointclouds, # background
              '0': o3d.geometry.pointclouds, # foreground
              '1': o3d.geometry.pointclouds, # (optional) foreground 2
              ...etc.}

        pcd_denoised -> same as pcd_dict
            {'-1': o3d.geometry.pointclouds, # background denoised
              '0': o3d.geometry.pointclouds, # foreground denoised
              '1': o3d.geometry.pointclouds, # (optional) foreground 2 denoised
              ...etc.}

        pcd_segmented -> similar with pcd_dict
            {'0': [o3d.geometry.pointclouds, o3d.geometry.pointclouds, ...],  # background -1 not included
             '1': [o3d.geometry.pointclouds, o3d.geometry.pointclouds, ...].  # (optional)
             ... etc. }

    Functions:
        classifier_apply: apply the specified classifier.
            [params]
                clf: the Classifier class
            [return]
                self.pcd_classified

        remove_noise: apply the noise filtering algorithms to both background and foregrounds
            [param]

            [return]
                self.pcd_denoised

        auto_segmentation: segment the foreground by automatic point clouds algorithm (DBSCAN)
            please note, this may include some noises depends on how the classifier and auto-denoise parameters
            [param]
                denoise: whether remove some outlier points which has high possibility to be noises not removed
            [return]
                self.pcd_segmented

        shp_segmentation: segment the foreground by given shp file instead of using auto segmentation.
            [param]
                shp_dir: the path of shp file
            [return]
                self.pcd_segmented
    """

    def __init__(self, ply_path, clf, output_path='.'):
        self.ply_path = ply_path
        self.pcd = read_ply(ply_path)
        self.folder, tail = os.path.split(os.path.abspath(self.ply_path))
        self.ply_name = tail[:-4]
        print(f'[3DPhenotyping][Plot][__init__] Ply file "{self.ply_path}" loaded')

        self.out_folder = os.path.join(output_path, self.ply_name)
        print(f'[3DPhenotyping][Plot][__init__] Setting output folder "{self.out_folder}"')
        make_dir(self.out_folder, clean=True)

        self.pcd_xyz = np.asarray(self.pcd.points)
        self.pcd_rgb = np.asarray(self.pcd.colors)

        self.classifier_apply(clf)
        self.pcd_cleaned, _ = self.remove_noise()

    def classifier_apply(self, clf):
        print('[3DPhenotyping][Plot][Classifier_apply] Start Classifying')
        pred_result = clf.predict(self.pcd_rgb)

        self.pcd_dict = {}

        for k in clf.kind_set:
            print(f'[3DPhenotyping][Plot][Classifier_apply] Begin for class {k}')
            indices = np.where(pred_result == k)[0].tolist()
            self.pcd_dict[k] = self.pcd.select_down_sample(indices=indices)
            print(f'[3DPhenotyping][Plot][Classifier_apply] kind {k} classified')
            # save ply
            o3d.io.write_point_cloud(os.path.join(self.out_folder, f'class[{k}].ply'),
                                     self.pcd_dict[k])

        return self.pcd_dict

    def remove_noise(self, part=100):
        self.pcd_voxel, self.voxel_size, self.voxel_density = pcd2voxel(self.pcd, part=part)

        pcd_cleaned = {}
        pcd_cleaned_id = {}
        print('[3DPhenotyping][Plot][remove_noise] Remove noises')
        for k in self.pcd_dict.keys():
            if k == -1:   # for background, need to apply statistical outlier removal
                cleaned, indices = self.pcd_dict[-1].remove_statistical_outlier\
                    (nb_neighbors=round(self.voxel_density), std_ratio=0.01)
                pcd_cleaned[-1], pcd_cleaned_id[-1] = cleaned.remove_radius_outlier\
                    (nb_points=round(self.voxel_density*2), radius=self.voxel_size)
            else:
                pcd_cleaned[k], pcd_cleaned_id[k] = self.pcd_dict[k].remove_radius_outlier\
                    (nb_points=round(self.voxel_density), radius=self.voxel_size)
            # save ply
            o3d.io.write_point_cloud(os.path.join(self.out_folder, f'class[{k}]-rm_noise.ply'),
                                     pcd_cleaned[k])
            # todo: add kde of ground points, and remove noises very close to ground points
            print(f'[3DPhenotyping][Plot][remove_noise] kind {k} noise removed')

        return pcd_cleaned, pcd_cleaned_id

    def auto_segmentation(self, denoise=True):
        # may need user to provide plant size and number for segmentation check
        seg_out = {}
        for k in self.pcd_dict.keys():
            # skip the background
            if k == -1:
                continue

            print(f'[3DPhenotyping][Plot][AutoSegment] Start segmenting class {k} Please wait...')
            vect = self.pcd_cleaned[k].cluster_dbscan(eps=self.voxel_size * 10,
                                                      min_points=round(self.voxel_density),
                                                      print_progress=True)
            vect_np = np.asarray(vect)
            seg_id = np.unique(vect_np)

            print(f'[3DPhenotyping][Plot][AutoSegment] class {k} Segmented')

            # KMeans to find the class of noise and plants
            # # Data prepare for clustering
            pcd_seg_list = []
            pcd_seg_char = np.empty((0, 2))

            for seg in seg_id:
                indices = np.where(vect_np == seg)[0].tolist()
                pcd_seg = self.pcd_cleaned[k].select_down_sample(indices)

                pcd_seg_list.append(pcd_seg)
                # todo: add mean height as a parameter
                char = np.asarray([len(pcd_seg.points) ** 0.5,
                                   calculate_xyz_volume(pcd_seg)])
                pcd_seg_char = np.vstack([pcd_seg_char, char])

            print(f'[3DPhenotyping][Plot][AutoSegment][Clustering] class {k} Cluster Data Prepared')

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

            temp_df = pd.DataFrame({'seg_id':[p for p in plant_id],
                                    'x':[pcd_seg_list[p].get_center()[0] for p in plant_id],
                                    'y':[pcd_seg_list[p].get_center()[0] for p in plant_id]})
            temp_df = temp_df.sort_values(by=['x', 'y']).reset_index()

            seg_out[k] = []
            for i, s_id in enumerate(temp_df['seg_id']):
                seg_out[k].append(pcd_seg_list[s_id])
                file_name = f'class[{k}]-plant{i}.ply'
                file_path = os.path.join(self.out_folder, file_name)
                print(f'[3DPhenotyping][Plot][AutoSegment][Output] writing file "{file_path}"')
                o3d.io.write_point_cloud(file_path, pcd_seg_list[s_id])

            print(f'[3DPhenotyping][Plot][AutoSegment][Clustering] class {k} Clustered')

        return seg_out

    def shp_segmentation(self, shp_dir):
        pass
        # return seg_out

    def write_figs(self, savepath=None):
        pass
        print('rua')


class Plant(object):
    # todo: ground point cloud parameters, can cut ground by convex hull
    def __init__(self, pcd_input, indices, ground_pcd, cut_bg=False, container_ht=0):
        if isinstance(pcd_input, str):
            self.pcd = read_ply(pcd_input)
        else:
            self.pcd = pcd_input
        self.center = self.pcd.get_center()

        self.pcd_xyz = np.asarray(self.pcd.points)
        self.pcd_rgb = np.asarray(self.pcd.colors)

        if isinstance(ground_pcd, str):   # type the ground point pcd
            self.ground_pcd = read_ply(ground_pcd)
        else:
            self.ground_pcd = ground_pcd

        # clip the background
        if cut_bg:
            self.clip_background()
            print(f'[3DPhenotyping][Plant][clip_background] finished for No. {indices}')

        print(f'[3DPhenotyping][Plant][Traits] No. {indices} Calculating')
        # calculate the convex hull 2d
        self.plane_hull, self.hull_area = convex_hull2d(self.pcd)  # vertex_set (2D ndarray), m^2

        # calculate min_area_bounding_rectangle,
        # rect_res = (rot_angle, area, width, length, center_point, corner_points)
        self.rect_res = min_bounding_rect(self.plane_hull)
        self.width = self.rect_res[2]   # unit is m
        self.length = self.rect_res[3]   # unit is m


        # calculate the projected 2D image (X-Y)
        binary, px_num_per_cm, corner = pcd2binary(self.pcd)
        # calculate region props
        self.centroid, self.major_axis, self.minor_axis, self.orient_degree = self.get_region_props(binary,
                                                                                                    px_num_per_cm,
                                                                                                    corner)
        # calculate projected leaf area
        self.pla_img = binary
        self.pla = self.get_projected_leaf_area(binary, px_num_per_cm)

        # calcuate percentile height
        self.pctl_ht, self.pctl_ht_plot = self.get_percentile_height(container_ht)


    def clip_background(self):
        x_max = self.pcd_xyz[:, 0].max()
        x_min = self.pcd_xyz[:, 0].min()
        x_len = x_max - x_min
        y_max = self.pcd_xyz[:, 1].max()
        y_min = self.pcd_xyz[:, 1].min()
        y_len = y_max - y_min

        polygon = np.array([[x_min - x_len*0.1, y_min - y_len*0.1, 0],
                            [x_min - x_len*0.1, y_max + y_len*0.1, 0],
                            [x_max + x_len*0.1, y_max + y_len*0.1, 0],
                            [x_max + x_len*0.1, y_min - y_len*0.1, 0],
                            [x_min - x_len*0.1, y_min - y_len*0.1, 0]])

        ground_xyz = np.asarray(self.ground_pcd.points)
        z_max = ground_xyz[:, 2].max()
        z_min = ground_xyz[:, 2].min()

        boundary = build_cut_boundary(polygon, (z_min, z_max))

        self.ground_pcd = boundary.crop_point_cloud(self.ground_pcd)

    # -=-=-=-=-=-=-=-=-=-=-=-=
    # | traits from 2D image |
    # -=-=-=-=-=-=-=-=-=-=-=-=

    def get_region_props(self, binary, px_num_per_cm, corner):
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

        return center, major_axis, minor_axis, angle

    def get_projected_leaf_area(self, binary, px_num_per_cm):
        kind, number = np.unique(binary, return_counts=True)
        # back_num = number[0]
        fore_num = number[1]

        pixel_size = (1 / px_num_per_cm) ** 2   # unit is cm2

        return fore_num * pixel_size

    # -=-=-=-=-=-=-=-=-=-=-=-=-
    # | traits from 3D points |
    # -=-=-=-=-=-=-=-=-=-=-=-=-
    def get_percentile_height(self, container_ht=0):
        z = self.pcd_xyz[:, 2]
        ground_z = np.asarray(self.ground_pcd.points)[:, 2]

        # calculate the ground center of Z, by mean of [per5 - per 90],
        # to avoid the effects of elevation and noises in upper part
        ele = ground_z[np.logical_and(ground_z < np.percentile(ground_z, 90),
                                      ground_z > np.percentile(ground_z, 5))].mean()
        plant_base = ele + container_ht

        ele_z = z[z > plant_base]
        top10percentile = np.percentile(ele_z, 90)
        plant_top = ele_z[ele_z > top10percentile].mean()

        percentile_ht = plant_top - plant_base

        plot_use = {'plant_top':plant_top, 'plant_base':plant_base,
                    'top10': top10percentile, 'ground_center':ele}

        return percentile_ht, plot_use
