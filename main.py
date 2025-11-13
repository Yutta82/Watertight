import trimesh

from Detector.HoleDetector import HoleDetector
from Repairer.HoleRepairer import HoleRepairer
from utils.chamfer_distance import calculate_chamfer_distance
from utils.visual import show_two_meshes_with_holes


def main():
    mesh = trimesh.load_mesh(r"c3_mesh_2.obj")
    hd = HoleDetector(mesh)
    hole_loops = hd.detect_holes_2()
    # hd.visual()
    repairer = HoleRepairer(mesh)
    repaired_mesh = repairer.repair_all_holes(hole_loops, method='planar')
    chamfer_dist, d1_to_2, d2_to_1 = calculate_chamfer_distance(mesh, repaired_mesh, 20000)
    print(chamfer_dist)
    show_two_meshes_with_holes(mesh, repaired_mesh, chamfer_dist, hd.get_hole_loop())
    print(repaired_mesh.is_watertight)


if __name__ == '__main__':
    main()
