from collections import defaultdict
from typing import List, Dict, Tuple, Set

import trimesh
import vedo


class HoleDetector:
    def __init__(self, mesh: trimesh.Trimesh):
        self.mesh = mesh
        self.mesh = mesh
        self.boundary_edges = []  # 存储边界边 [(v1, v2), ...]
        self.hole_loops = []  # 存储孔洞环 [ [v1, v2, v3, ...], ... ]
        self.edge_to_faces = defaultdict(list)  # 边到面的映射
        self.boundary_vertices = set()  # 边界顶点集合

    def find_boundary_edges(self) -> List[Tuple[int, int]]:
        """查找所有的边界边"""
        print("Finding boundary edges...")

        # 清空之前的数据
        self.boundary_edges = []
        self.edge_to_faces.clear()
        self.boundary_vertices.clear()

        # 构建边到面的映射
        for face_idx, face in enumerate(self.mesh.faces):
            # 面的三条边（排序以确保一致性）
            edges = [
                tuple(sorted([face[0], face[1]])),
                tuple(sorted([face[1], face[2]])),
                tuple(sorted([face[2], face[0]]))
            ]

            for edge in edges:
                self.edge_to_faces[edge].append(face_idx)

        # 找出边界边（只被一个面共享的边）
        for edge, face_list in self.edge_to_faces.items():
            if len(face_list) == 1:
                self.boundary_edges.append(edge)
                self.boundary_vertices.add(edge[0])
                self.boundary_vertices.add(edge[1])

        print(f"Found {len(self.boundary_edges)} boundary edges")
        print(f"Found {len(self.boundary_vertices)} boundary vertices")
        return self.boundary_edges

    def build_edge_graph(self) -> Dict[int, List[int]]:
        """构建边界边的图结构"""
        edge_graph = defaultdict(list)

        for edge in self.boundary_edges:
            v1, v2 = edge
            edge_graph[v1].append(v2)
            edge_graph[v2].append(v1)

        return edge_graph

    def trace_hole_loop(self, start_vertex: int, visited_vertices: Set[int],
                        edge_graph: Dict[int, List[int]]) -> List[int]:
        """从起始顶点追踪一个完整的孔洞环"""
        hole_loop = []
        current_vertex = start_vertex

        while current_vertex not in visited_vertices:
            visited_vertices.add(current_vertex)
            hole_loop.append(current_vertex)

            # 查找下一个顶点
            neighbors = edge_graph[current_vertex]
            unvisited_neighbors = [v for v in neighbors if v not in visited_vertices]

            if not unvisited_neighbors:
                # 如果没有未访问的邻居，尝试闭合环
                if hole_loop[0] in neighbors:
                    hole_loop.append(hole_loop[0])  # 闭合环
                break

            # 移动到下一个未访问的顶点
            current_vertex = unvisited_neighbors[0]

        return hole_loop

    def trace_hole_loop_improved(self, start_vertex: int, visited_edges: Set[Tuple[int, int]],
                                 adjacency: Dict[int, List[int]]) -> List[int]:
        """改进的孔洞环追踪算法"""
        loop = [start_vertex]
        current = start_vertex
        prev = None

        while True:
            neighbors = adjacency[current]

            # 过滤掉已访问的边和前一个顶点
            available_neighbors = []
            for neighbor in neighbors:
                edge = tuple(sorted([current, neighbor]))
                if edge not in visited_edges and neighbor != prev:
                    available_neighbors.append(neighbor)

            if not available_neighbors:
                break

            # 选择下一个顶点（如果有多个选择，选择第一个）
            next_vertex = available_neighbors[0]

            # 标记边为已访问
            edge = tuple(sorted([current, next_vertex]))
            visited_edges.add(edge)

            # 检查是否回到起点
            if next_vertex == start_vertex and len(loop) > 2:
                loop.append(start_vertex)  # 闭合环
                break

            # 检查是否已经访问过这个顶点（避免无限循环）
            if next_vertex in loop:
                break

            loop.append(next_vertex)
            prev = current
            current = next_vertex

            # 安全检查：防止无限循环
            if len(loop) > len(self.boundary_vertices):
                print("Warning: Loop too long, breaking")
                break

        return loop

    def find_all_cycles_dfs(self, adjacency: Dict[int, List[int]]) -> List[List[int]]:
        """使用深度优先搜索查找所有环"""
        all_cycles = []
        visited_edges = set()

        def dfs_cycle(current: int, path: List[int], start: int, visited_in_path: Set[int]) -> None:
            if len(path) > 1 and current == start:
                # 找到一个环
                cycle = path + [start]
                if len(cycle) > 3:  # 至少3个不同顶点的环
                    all_cycles.append(cycle[:])
                return

            if current in visited_in_path and current != start:
                return  # 避免在同一路径中重复访问

            if len(path) > len(self.boundary_vertices):
                return  # 防止无限递归

            visited_in_path.add(current)

            for neighbor in adjacency[current]:
                edge = tuple(sorted([current, neighbor]))

                # 如果这条边还没被用过，或者neighbor是起始点（闭合环）
                if edge not in visited_edges or (neighbor == start and len(path) > 2):
                    if neighbor == start and len(path) > 2:
                        # 闭合环
                        dfs_cycle(neighbor, path, start, visited_in_path)
                    elif neighbor not in visited_in_path:
                        # 继续搜索
                        visited_edges.add(edge)
                        dfs_cycle(neighbor, path + [current], start, visited_in_path)
                        visited_edges.remove(edge)

            visited_in_path.remove(current)

        # 从每个边界顶点开始搜索
        for start_vertex in sorted(self.boundary_vertices):
            visited_edges.clear()
            dfs_cycle(start_vertex, [], start_vertex, set())

        return all_cycles

    def filter_hole_loops(self):
        """过滤和清理孔洞环"""
        valid_loops = []
        seen_vertices = set()

        for loop in self.hole_loops:
            # 检查环是否有效（闭合且无重复顶点，除了首尾）
            if len(loop) < 4 or loop[0] != loop[-1]:
                continue

            # 检查中间顶点是否重复
            middle_vertices = set(loop[:-1])
            if len(middle_vertices) != len(loop) - 1:
                continue

            # 检查是否已经包含在其他环中
            loop_vertices = set(loop)
            if not loop_vertices.intersection(seen_vertices):
                valid_loops.append(loop)
                seen_vertices.update(loop_vertices)

        self.hole_loops = valid_loops

    def build_hole_loops(self) -> List[List[int]]:
        """构建所有的孔洞环"""
        print("Building hole loops...")

        if not self.boundary_edges:
            self.find_boundary_edges()

        edge_graph = self.build_edge_graph()
        visited_vertices = set()
        self.hole_loops = []

        # 对每个边界顶点进行追踪
        for vertex in self.boundary_vertices:
            if vertex not in visited_vertices:
                hole_loop = self.trace_hole_loop_improved(vertex, visited_vertices, edge_graph)

                # 确保环是闭合的且长度足够
                if len(hole_loop) >= 3:
                    # 检查是否闭合
                    if hole_loop[0] != hole_loop[-1]:
                        # 如果不闭合，尝试连接首尾
                        if hole_loop[0] in edge_graph[hole_loop[-1]]:
                            hole_loop.append(hole_loop[0])

                    # 只有闭合的环才被认为是有效的孔洞
                    if hole_loop[0] == hole_loop[-1] and len(hole_loop) > 3:
                        self.hole_loops.append(hole_loop)

        # 过滤掉重复或无效的环
        # self.filter_hole_loops()

        print(f"Found {len(self.hole_loops)} hole loops")
        # for i, loop in enumerate(self.hole_loops):
        #     print(f"Hole {i + 1}: {len(loop) - 1} edges")

        return self.hole_loops

    def build_hole_loops_2(self) -> List[List[int]]:
        """构建所有的孔洞环 - 使用改进算法"""
        print("Building hole loops...")

        if not self.boundary_edges:
            self.find_boundary_edges()

        # 使用邻接图
        adjacency = self.build_adjacency_graph()

        # 方法1：改进的追踪算法
        visited_edges = set()
        loops_method1 = []

        for start_vertex in sorted(self.boundary_vertices):
            # 检查这个顶点是否还有未使用的边
            has_unused_edges = False
            for neighbor in adjacency[start_vertex]:
                edge = tuple(sorted([start_vertex, neighbor]))
                if edge not in visited_edges:
                    has_unused_edges = True
                    break

            if has_unused_edges:
                loop = self.trace_hole_loop_improved(start_vertex, visited_edges, adjacency)
                if len(loop) > 3 and loop[0] == loop[-1]:
                    loops_method1.append(loop)

        # 方法2：深度优先搜索（备用方法）
        loops_method2 = self.find_all_cycles_dfs(adjacency)

        # 合并结果并去重
        all_loops = loops_method1 + loops_method2
        self.hole_loops = self.deduplicate_loops(all_loops)

        print(f"Found {len(self.hole_loops)} hole loops")
        for i, loop in enumerate(self.hole_loops):
            print(f"Hole {i + 1}: {len(loop) - 1} vertices")

        return self.hole_loops

    def validate_loops(self) -> List[List[int]]:
        """验证环的有效性"""
        valid_loops = []

        for loop in self.hole_loops:
            if self.is_valid_loop(loop):
                valid_loops.append(loop)
            else:
                print(f"Invalid loop found: {loop}")

        return valid_loops

    def is_valid_loop(self, loop: List[int]) -> bool:
        """检查环是否有效"""
        if len(loop) < 4:
            return False

        if loop[0] != loop[-1]:
            return False

        # 检查所有边是否都是边界边
        for i in range(len(loop) - 1):
            edge = tuple(sorted([loop[i], loop[i + 1]]))
            if edge not in [tuple(sorted(be)) for be in self.boundary_edges]:
                return False

        # 检查中间顶点是否有重复
        middle_vertices = loop[:-1]
        if len(set(middle_vertices)) != len(middle_vertices):
            return False

        return True

    def detect_holes(self) -> List[List[int]]:
        """完整的孔洞检测流程"""
        self.find_boundary_edges()
        self.build_hole_loops()
        return self.hole_loops

    def detect_holes_2(self) -> List[List[int]]:
        """完整的孔洞检测流程"""
        print("Starting hole detection...")
        self.find_boundary_edges()

        if not self.boundary_edges:
            print("No boundary edges found - mesh appears to be closed")
            return []

        self.build_hole_loops()
        valid_loops = self.validate_loops()

        print(f"Final result: {len(valid_loops)} valid holes detected")
        return valid_loops
        # return self.build_hole_loops()

    def get_hole_info(self) -> Dict:
        pass

    def visual(self, show_original=True, highlight_holes=True, title=None):
        """使用vedo可视化孔洞检测结果（简化稳定版）"""
        # 创建vedo网格对象
        vedo_mesh = vedo.Mesh([self.mesh.vertices, self.mesh.faces])
        vedo_mesh.color('lightblue').alpha(0.8)
        vedo_mesh.linewidth(1)

        plots = [vedo_mesh] if show_original else []

        if highlight_holes and self.hole_loops:
            # 为每个孔洞创建高亮的边界线
            for i, hole_loop in enumerate(self.hole_loops):
                if len(hole_loop) < 2:
                    continue

                # 获取孔洞边界的顶点坐标
                hole_vertices = self.mesh.vertices[hole_loop]
                # 创建孔洞边界线
                hole_line = vedo.Line(hole_vertices, closed=True)
                hole_line.color('red').linewidth(5)
                plots.append(hole_line)

        # 设置标题
        if title is None:
            title = f"Hole Detection Results: {len(self.hole_loops)} holes, {len(self.boundary_edges)} edges"

        # 显示结果
        vedo.show(plots, title, axes=1, bg='white', size=(1200, 800))


if __name__ == '__main__':
    # mesh = trimesh.load_mesh(r"D:\University\Post\HunYuan3D_test_cases\test_cases\chaos.obj")
    mesh = trimesh.load_mesh(r"c3_mesh.obj")
    hd = HoleDetector(mesh)
    hd.detect_holes_2()
    hd.visual()
