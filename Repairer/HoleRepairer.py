from typing import List, Optional

import numpy as np
import trimesh
from scipy.spatial import Delaunay


class HoleRepairer:
    def __init__(self, mesh: trimesh.Trimesh):
        """
        初始化孔洞修复器

        Args:
            mesh: 输入的trimesh网格对象
        """
        self.mesh = mesh
        self.repaired_mesh = None

    def repair_hole(self, hole_loop: List[int], method: str = 'planar') -> trimesh.Trimesh:
        """
        修复单个孔洞

        Args:
            hole_loop: 孔洞环的顶点索引列表（首尾相同表示闭合）
            method: 修复方法 ('planar', 'advancing_front', 'minimal_surface')

        Returns:
            修复后的mesh
        """
        if len(hole_loop) < 4:
            print("Warning: Hole loop too short to repair")
            return self.mesh

        # 移除重复的首尾顶点
        if hole_loop[0] == hole_loop[-1]:
            hole_loop = hole_loop[:-1]

        if method == 'planar':
            return self.repair_planar(hole_loop)
        elif method == 'advancing_front':
            return self.repair_advancing_front(hole_loop)
        elif method == 'minimal_surface':
            return self.repair_minimal_surface(hole_loop)
        else:
            raise ValueError(f"Unknown repair method: {method}")

    def repair_planar(self, hole_loop: List[int]) -> trimesh.Trimesh:
        """
        使用平面三角化方法修复孔洞
        将孔洞投影到最佳拟合平面，然后进行三角化
        """
        # 获取孔洞边界顶点
        boundary_vertices = self.mesh.vertices[hole_loop]

        # 计算最佳拟合平面
        center = np.mean(boundary_vertices, axis=0)
        centered_vertices = boundary_vertices - center

        # 使用SVD找到法向量
        _, _, vh = np.linalg.svd(centered_vertices)
        normal = vh[-1]  # 最小奇异值对应的向量

        # 创建平面坐标系
        u = self.get_perpendicular(normal)
        u = u / np.linalg.norm(u)
        v = np.cross(normal, u)
        v = v / np.linalg.norm(v)

        # 将3D点投影到2D
        points_2d = np.column_stack([
            np.dot(centered_vertices, u),
            np.dot(centered_vertices, v)
        ])

        # 使用Delaunay三角化
        try:
            tri = Delaunay(points_2d)
            triangles = tri.simplices
        except Exception as e:
            print(f"Delaunay triangulation failed: {e}")
            return self.mesh

        # 创建新面（映射回原始顶点索引）
        new_faces = []
        for triangle in triangles:
            face_indices = [hole_loop[i] for i in triangle]
            # 确保法向量方向一致
            if self.check_face_orientation(face_indices, normal):
                new_faces.append(face_indices)
            else:
                new_faces.append(face_indices[::-1])

        # 合并到原始mesh
        all_faces = np.vstack([self.mesh.faces, new_faces])
        repaired_mesh = trimesh.Trimesh(
            vertices=self.mesh.vertices,
            faces=all_faces,
            process=False
        )

        return repaired_mesh

    def repair_advancing_front(self, hole_loop: List[int]) -> trimesh.Trimesh:
        """
        使用推进前沿法修复孔洞
        从边界逐步向内部推进，创建三角形
        """
        boundary = hole_loop.copy()
        new_faces = []

        while len(boundary) > 3:
            # 找到最优的三角形
            best_idx = self.find_best_triangle(boundary)

            if best_idx is None:
                break

            # 创建三角形
            n = len(boundary)
            v1 = boundary[best_idx]
            v2 = boundary[(best_idx + 1) % n]
            v3 = boundary[(best_idx + 2) % n]

            new_faces.append([v1, v2, v3])

            # 从边界移除中间顶点
            boundary.pop((best_idx + 1) % n)

        # 添加最后的三角形
        if len(boundary) == 3:
            new_faces.append(boundary)

        # 合并到原始mesh
        all_faces = np.vstack([self.mesh.faces, new_faces])
        repaired_mesh = trimesh.Trimesh(
            vertices=self.mesh.vertices,
            faces=all_faces,
            process=False
        )

        return repaired_mesh

    def repair_minimal_surface(self, hole_loop: List[int]) -> trimesh.Trimesh:
        """
        使用最小曲面方法修复孔洞
        这里使用简化版本：结合平面三角化和平滑
        """
        # 首先使用平面方法修复
        repaired_mesh = self.repair_planar(hole_loop)

        # 对新添加的顶点进行拉普拉斯平滑
        # 这里暂时返回平面修复结果
        return repaired_mesh

    def find_best_triangle(self, boundary: List[int]) -> Optional[int]:
        """
        在推进前沿法中找到最佳的三角形位置
        选择最小角度最大的三角形（避免细长三角形）
        """
        n = len(boundary)
        if n < 3:
            return None

        best_idx = 0
        best_min_angle = -1

        for i in range(n):
            v1 = self.mesh.vertices[boundary[i]]
            v2 = self.mesh.vertices[boundary[(i + 1) % n]]
            v3 = self.mesh.vertices[boundary[(i + 2) % n]]

            # 计算三角形的最小角度
            min_angle = self.compute_min_angle(v1, v2, v3)

            if min_angle > best_min_angle:
                best_min_angle = min_angle
                best_idx = i

        return best_idx

    def compute_min_angle(self, v1: np.ndarray, v2: np.ndarray, v3: np.ndarray) -> float:
        """计算三角形的最小角度"""
        edges = [v2 - v1, v3 - v2, v1 - v3]
        edge_lengths = [np.linalg.norm(e) for e in edges]

        # 避免除零
        if any(l < 1e-10 for l in edge_lengths):
            return 0.0

        # 使用余弦定理计算角度
        angles = []
        for i in range(3):
            a, b, c = edge_lengths[i], edge_lengths[(i + 1) % 3], edge_lengths[(i + 2) % 3]
            cos_angle = (b ** 2 + c ** 2 - a ** 2) / (2 * b * c)
            cos_angle = np.clip(cos_angle, -1.0, 1.0)
            angle = np.arccos(cos_angle)
            angles.append(angle)

        return min(angles)

    def get_perpendicular(self, normal: np.ndarray) -> np.ndarray:
        """获取与法向量垂直的向量"""
        if abs(normal[0]) < 0.9:
            return np.cross(normal, [1, 0, 0])
        else:
            return np.cross(normal, [0, 1, 0])

    def check_face_orientation(self, face_indices: List[int], target_normal: np.ndarray) -> bool:
        """检查面的法向量方向是否与目标一致"""
        v0 = self.mesh.vertices[face_indices[0]]
        v1 = self.mesh.vertices[face_indices[1]]
        v2 = self.mesh.vertices[face_indices[2]]

        edge1 = v1 - v0
        edge2 = v2 - v0
        face_normal = np.cross(edge1, edge2)

        if np.linalg.norm(face_normal) < 1e-10:
            return True

        face_normal = face_normal / np.linalg.norm(face_normal)
        return np.dot(face_normal, target_normal) > 0

    def repair_all_holes(self, hole_loops: List[List[int]], method: str = 'planar') -> trimesh.Trimesh:
        """
        修复所有孔洞

        Args:
            hole_loops: 所有孔洞的顶点索引列表
            method: 修复方法

        Returns:
            完全修复后的mesh
        """
        # print(f"Repairing {len(hole_loops)} holes using {method} method...")

        repaired_mesh = self.mesh.copy()

        for i, hole_loop in enumerate(hole_loops):
            print(f"Repairing hole {i + 1}/{len(hole_loops)}...")
            # 更新当前mesh
            self.mesh = repaired_mesh
            repaired_mesh = self.repair_hole(hole_loop, method)

        self.repaired_mesh = repaired_mesh
        print("All holes repaired!")

        return repaired_mesh

    def get_repair_stats(self) -> dict:
        """获取修复统计信息"""
        if self.repaired_mesh is None:
            return {"status": "No repair performed"}

        original_faces = len(self.mesh.faces)
        repaired_faces = len(self.repaired_mesh.faces)
        added_faces = repaired_faces - original_faces

        return {
            "original_faces": original_faces,
            "repaired_faces": repaired_faces,
            "added_faces": added_faces,
            "is_watertight": self.repaired_mesh.is_watertight
        }

    def save_repaired_mesh(self, filepath: str):
        """保存修复后的mesh"""
        if self.repaired_mesh is None:
            print("No repaired mesh to save. Please run repair first.")
            return

        self.repaired_mesh.export(filepath)
        print(f"Repaired mesh saved to {filepath}")
