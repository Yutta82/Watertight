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
