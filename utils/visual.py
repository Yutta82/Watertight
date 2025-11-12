import trimesh
import vedo


def show_mesh(mesh,
              color='lightblue',
              alpha=1.0,
              wireframe=False,
              show_edges=False,
              edge_color='black',
              title='Mesh Visualization',
              axes=1,
              bg='white',
              size=(1200, 800),
              camera_pos=None):
    """
    使用vedo可视化trimesh网格

    Args:
        mesh: trimesh.Trimesh对象或vedo.Mesh对象
        color: 网格颜色，默认'lightblue'
        alpha: 透明度，0-1之间，默认1.0
        wireframe: 是否显示为线框模式，默认False
        show_edges: 是否显示边缘线，默认False
        edge_color: 边缘线颜色，默认'black'
        title: 窗口标题
        axes: 坐标轴显示方式 (0=不显示, 1=简单坐标轴, 4-13=不同样式)
        bg: 背景颜色，默认'white'
        size: 窗口大小 (width, height)
        camera_pos: 相机位置，例如 (x, y, z) 或 None
    """
    # 如果是trimesh对象，转换为vedo对象
    if isinstance(mesh, trimesh.Trimesh):
        vedo_mesh = vedo.Mesh([mesh.vertices, mesh.faces])
    else:
        vedo_mesh = mesh

    # 设置颜色和透明度
    vedo_mesh.color(color).alpha(alpha)

    # 线框模式
    if wireframe:
        vedo_mesh.wireframe(True)

    # 显示边缘
    if show_edges:
        vedo_mesh.linewidth(1).linecolor(edge_color)

    # 创建绘图对象列表
    plots = [vedo_mesh]

    # 显示
    plotter = vedo.show(plots,
                        title=title,
                        axes=axes,
                        bg=bg,
                        size=size,
                        interactive=True)

    return plotter


def show_two_meshes_with_holes(mesh1, mesh2, hole_loops=None,
                               title1="Original Mesh", title2="Repaired Mesh",
                               highlight_holes=True):
    """
    使用vedo同时展示两个网格，可以高亮显示孔洞

    Args:
        mesh1: 第一个网格对象（trimesh）
        mesh2: 第二个网格对象（trimesh）
        hole_loops: 原始网格的孔洞边界循环列表
        title1: 第一个网格的标题
        title2: 第二个网格的标题
        highlight_holes: 是否高亮显示孔洞
    """
    # 创建第一个网格的可视化
    vedo_mesh1 = vedo.Mesh([mesh1.vertices, mesh1.faces])
    vedo_mesh1.color('lightblue').alpha(0.8)
    vedo_mesh1.linewidth(1)

    plots1 = [vedo_mesh1]

    # 高亮第一个网格的孔洞
    if highlight_holes and hole_loops:
        for i, hole_loop in enumerate(hole_loops):
            if len(hole_loop) < 2:
                continue
            hole_vertices = mesh1.vertices[hole_loop]
            hole_line = vedo.Line(hole_vertices, closed=True)
            hole_line.color('red').linewidth(5)
            plots1.append(hole_line)

    # 在第一个网格上添加标题文本
    title_text1 = vedo.Text2D(
        f"{title1}\nHoles: {len(hole_loops) if hole_loops else 0}",
        pos='top-center',
        c='black',
        s=1.2,
        bg='white',
        alpha=0.8
    )
    plots1.append(title_text1)

    # 创建第二个网格的可视化
    vedo_mesh2 = vedo.Mesh([mesh2.vertices, mesh2.faces])
    vedo_mesh2.color('lightgreen').alpha(0.8)
    vedo_mesh2.linewidth(1)

    plots2 = [vedo_mesh2]

    # 在第二个网格上添加标题文本
    title_text2 = vedo.Text2D(
        f"{title2}",
        pos='top-center',
        c='black',
        s=1.2,
        bg='white',
        alpha=0.8
    )
    plots2.append(title_text2)

    # 并排显示两个网格
    vedo.show([plots1, plots2], N=2, axes=1, bg='white', size=(1600, 800))

def show_mesh_info(mesh: trimesh.Trimesh):
    return [len(mesh.vertices), len(mesh.edges_unique), len(mesh.faces)]
