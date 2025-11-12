import trimesh


def mesh_output(mesh: trimesh.Trimesh, path: str, file_name: str="repaired.obj"):
    mesh.export(path + file_name)