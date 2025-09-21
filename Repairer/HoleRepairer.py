import trimesh


class HoleRepairer:
    def __init__(self, mesh: trimesh.Trimesh):
        self.mesh = mesh

    def repair_hole_simple(self):
        # 在洞的重心添加一个顶点,从重心向洞边界做扇形三角化
        pass

    def repair_hole_planar(self):
        # 将洞投影到最佳拟合平面
        pass

    def repair_hole_advancing_front(self):
        # 前进前沿法,逐步向内收缩边界
        pass
