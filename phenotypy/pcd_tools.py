import numpy as np
import open3d as o3d
from scipy.spatial import ConvexHull

def calculate_xyz_volume(pcd):
    pcd_xyz = np.asarray(pcd.points)

    x_len = pcd_xyz[:, 0].max() - pcd_xyz[:, 0].min()
    y_len = pcd_xyz[:, 1].max() - pcd_xyz[:, 1].min()
    z_len = pcd_xyz[:, 2].max() - pcd_xyz[:, 2].min()

    return x_len * y_len * z_len

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

def build_cut_boundary(polygon, z_range):
    """
    :param polygon: np.array shape=[n x 3]
    :param z_range: list or tuple, z_range=(z_min, z_max)
    """
    z_min = z_range[0]
    z_max = z_range[1]

    boundary = o3d.visualization.SelectionPolygonVolume()
    boundary.orthogonal_axis = "Z"
    boundary.bounding_polygon = o3d.utility.Vector3dVector(polygon)
    boundary.axis_max = z_max
    boundary.axis_min = z_min

    return boundary

def clip_pcd(pcd, boundary):
    pass

def convex_hull2d(pcd):
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
    pcd_xyz = np.asarray(pcd.points)
    xy = pcd_xyz[:, 0:2]
    hull = ConvexHull(xy)
    hull_volume = hull.volume
    hull_xy = xy[hull.vertices, :]
    return hull_xy, hull_volume

def pcd2dom(pcd, voxel_size):
    down_pcd = pcd.voxel_down_sample(voxel_size=voxel_size)
    pass

def pcd2binary(pcd, dpi=10):
    # dpi suggest < 20
    pcd_xyz = np.asarray(pcd.points)
    # !!!! notice !!!!
    # in numpy image system, Y axis is 0, X axis is 1
    y = pcd_xyz[:, 0]
    x = pcd_xyz[:, 1]

    x_length_m = x.max() - x.min()
    y_length_m = y.max() - y.min()
    px_num_per_cm = int(dpi / 2.54)
    width = int(np.ceil(x_length_m * 100 * px_num_per_cm))
    height = int(np.ceil(y_length_m * 100 * px_num_per_cm))
    ref_x = (x - x.min()) / x_length_m * width
    ref_y = (y - y.min()) / y_length_m * height
    ref_pos = np.vstack([ref_x, ref_y]).T.astype(int)
    ref_pos_rm_dup = np.unique(ref_pos, axis=0)

    out_img = np.zeros((width + 1, height + 1))
    out_img[ref_pos_rm_dup[:, 0], ref_pos_rm_dup[:, 1]] = 1
    out_img = out_img.astype(int)

    left_top_corner = (y.min(), x.min())

    return out_img, px_num_per_cm, left_top_corner

def pcd2voxel(pcd, part=100):
    pcd_xyz = np.asarray(pcd.points)
    points_num = pcd_xyz.shape[0]  # get the size of this plot

    x_max = pcd_xyz[:, 0].max()
    x_min = pcd_xyz[:, 0].min()
    x_len = x_max - x_min

    y_max = pcd_xyz[:, 1].max()
    y_min = pcd_xyz[:, 1].min()
    y_len = y_max - y_min

    z_max = pcd_xyz[:, 2].max()
    z_min = pcd_xyz[:, 2].min()
    z_len = z_max - z_min
    
    # param part: how many part of the shortest axis will be split?
    voxel_size = min(x_len, y_len, z_len) / part
    # convert point cloud to voxel
    pcd_voxel = o3d.geometry.VoxelGrid().create_from_point_cloud(pcd, voxel_size=voxel_size)

    voxel_num = len(pcd_voxel.voxels)
    voxel_density = points_num / voxel_num

    return pcd_voxel, voxel_size, voxel_density