import trimesh

from Detector.HoleDetector import HoleDetector
from Repairer.HoleRepairer import HoleRepairer
from utils.chamfer_distance import calculate_chamfer_distance
from utils.visual import show_mesh, show_two_meshes_with_holes


def main():
    mesh = trimesh.load_mesh(r"c3_mesh_2.obj")
    hd = HoleDetector(mesh)
    hole_loops = hd.detect_holes_2()
    repairer = HoleRepairer(mesh)
    repaired_mesh = repairer.repair_all_holes(hole_loops, method='planar')
    # show_mesh(repaired_mesh)
    show_two_meshes_with_holes(mesh, repaired_mesh, hd.get_hole_loop())
    chamfer_dist, d1_to_2, d2_to_1 = calculate_chamfer_distance(mesh, repaired_mesh, 1024)
    print(chamfer_dist)

if __name__ == '__main__':
    main()