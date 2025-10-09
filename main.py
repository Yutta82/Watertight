import trimesh

from Detector.HoleDetector import HoleDetector
from Repairer.HoleRepairer import HoleRepairer
from utils.visual import show_mesh


def main():
    mesh = trimesh.load_mesh(r"D:\University\Post\Data\BPT生成结果\dm\c3_mesh_2.obj")
    hd = HoleDetector(mesh)
    hole_loops = hd.detect_holes_2()
    repairer = HoleRepairer(mesh)
    repaired_mesh = repairer.repair_all_holes(hole_loops, method='planar')
    show_mesh(repaired_mesh)

if __name__ == '__main__':
    main()