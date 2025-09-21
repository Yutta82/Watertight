import trimesh


class HoleDetector:
    def __init__(self, mesh: trimesh.Trimesh):
        self.mesh = mesh
        pass

    def find_boundary_edges(self):
        pass

    def build_hole_loops(self):
        self.trace_hole_loop()
        pass

    def trace_hole_loop(self):
        pass

    def get_hole_info(self):
        pass

    def detect_holes(self):
        self.find_boundary_edges()
        self.build_hole_loops()