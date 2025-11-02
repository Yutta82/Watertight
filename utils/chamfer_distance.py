import trimesh
from scipy.spatial.distance import cdist
import numpy as np

def calculate_chamfer_distance(mesh1, mesh2, num_samples=None):
    """
    计算两个网格之间的倒角距离（Chamfer Distance）

    Args:
        mesh1: 第一个网格对象
        mesh2: 第二个网格对象

    Returns:
        chamfer_distance: 倒角距离
        d1_to_2: 从mesh1点到mesh2的平均距离
        d2_to_1: 从mesh2点到mesh1的平均距离
    """
    if num_samples is not None:
        points1, _ = trimesh.sample.sample_surface(mesh1, num_samples)
        points2, _ = trimesh.sample.sample_surface(mesh2, num_samples)
    else:
        # 否则使用网格顶点
        points1 = mesh1.vertices
        points2 = mesh2.vertices

    # 计算从mesh1到mesh2的最小距离
    distances1_to_2 = cdist(points1, points2, metric='euclidean')
    min_distances1_to_2 = np.min(distances1_to_2, axis=1)
    d1_to_2 = np.mean(min_distances1_to_2)

    # 计算从mesh2到mesh1的最小距离
    distances2_to_1 = cdist(points2, points1, metric='euclidean')
    min_distances2_to_1 = np.min(distances2_to_1, axis=1)
    d2_to_1 = np.mean(min_distances2_to_1)

    # 倒角距离是两个方向的平均
    chamfer_distance = (d1_to_2 + d2_to_1) / 2.0

    return chamfer_distance, d1_to_2, d2_to_1