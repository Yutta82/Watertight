import trimesh
from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for, send_from_directory
import os
import uuid
from werkzeug.utils import secure_filename
import tempfile
import shutil

from Detector.HoleDetector import HoleDetector
from Repairer.HoleRepairer import HoleRepairer
from utils.chamfer_distance import calculate_chamfer_distance
from utils.visual import show_mesh_info

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# 配置文件上传
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'obj', 'stl', 'ply', 'off', '3ds', 'fbx'}
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# 确保上传目录存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_file_info(filepath):
    """获取mesh文件的基本信息"""
    try:
        size = os.path.getsize(filepath)
        ext = filepath.rsplit('.', 1)[1].lower() if '.' in filepath else 'unknown'
        mesh = trimesh.load_mesh(filepath)
        msg = show_mesh_info(mesh)
        # 这里可以添加更详细的mesh文件解析逻辑
        # 目前返回模拟数据
        import random
        return {
            'vertices': msg[0],
            'faces': msg[2],
            'size': size,
            'format': ext.upper()
        }
    except:
        return {'vertices': 0, 'faces': 0, 'size': 0, 'format': 'Unknown'}


# 简化的侧边栏项目
sidebar_items = [
    {"name": "首页", "icon": "🏠", "url": "/", "active": True},
    {"name": "Mesh可视化", "icon": "🔍", "url": "/mesh-visualization", "active": False},
    {"name": "Mesh修补", "icon": "🔧", "url": "/mesh-repair", "active": False}
]

# 存储上传的文件信息
uploaded_files = {}


@app.route('/')
def index():
    items = sidebar_items.copy()
    items[0]["active"] = True
    items[1]["active"] = False
    items[2]["active"] = False
    return render_template('index.html',
                           sidebar_items=items,
                           uploaded_files=uploaded_files)


@app.route('/mesh-visualization', methods=['GET', 'POST'])
def mesh_visualization():
    items = sidebar_items.copy()
    items[0]["active"] = False
    items[1]["active"] = True
    items[2]["active"] = False

    if request.method == 'POST':
        # 处理文件上传
        if 'mesh_file' not in request.files:
            flash('没有选择文件', 'error')
            return redirect(request.url)

        file = request.files['mesh_file']

        if file.filename == '':
            flash('没有选择文件', 'error')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            # 生成唯一文件名
            file_id = str(uuid.uuid4())
            filename = secure_filename(file.filename)
            file_ext = filename.rsplit('.', 1)[1].lower()
            unique_filename = f"{file_id}.{file_ext}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)

            # 保存文件
            file.save(filepath)

            # 获取文件信息 - 这里添加了file_info
            file_info = get_file_info(filepath)

            # 存储文件信息 - 包含file_info
            uploaded_files[file_id] = {
                'original_name': filename,
                'saved_name': unique_filename,
                'filepath': filepath,
                'file_info': file_info,  # 添加这一行
                'upload_time': '刚刚'
            }

            flash(f'文件 "{filename}" 上传成功！', 'success')
            return jsonify({
                'success': True,
                'file_id': file_id,
                'filename': filename,
                'file_info': file_info  # 添加这一行
            })
        else:
            flash('不支持的文件格式。请上传 OBJ, STL, PLY, OFF, 3DS, FBX 格式的文件。', 'error')
            return jsonify({'success': False, 'error': '不支持的文件格式'})

    return render_template('mesh_visualization.html',
                           sidebar_items=items,
                           uploaded_files=uploaded_files)


@app.route('/mesh-repair', methods=['GET', 'POST'])
def mesh_repair():
    items = sidebar_items.copy()
    items[0]["active"] = False
    items[1]["active"] = False
    items[2]["active"] = True

    if request.method == 'POST':
        # 检查是否有文件被上传
        if 'mesh_file' not in request.files:
            flash('没有选择文件', 'error')
            return redirect(request.url)

        file = request.files['mesh_file']

        # 如果用户没有选择文件
        if file.filename == '':
            flash('没有选择文件', 'error')
            return redirect(request.url)

        # 检查文件类型
        if file and allowed_file(file.filename):
            # 生成唯一文件名
            file_id = str(uuid.uuid4())
            filename = secure_filename(file.filename)
            file_ext = filename.rsplit('.', 1)[1].lower()
            unique_filename = f"{file_id}.{file_ext}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)

            # 保存文件
            file.save(filepath)

            # 获取文件信息
            file_info = get_file_info(filepath)

            # 存储文件信息
            uploaded_files[file_id] = {
                'original_name': filename,
                'saved_name': unique_filename,
                'filepath': filepath,
                'file_info': file_info,
                'upload_time': '刚刚'
            }

            flash(f'文件 "{filename}" 上传成功！', 'success')
            return jsonify({
                'success': True,
                'file_id': file_id,
                'filename': filename,
                'file_info': file_info
            })
        else:
            flash('不支持的文件格式。请上传 OBJ, STL, PLY, OFF, 3DS, FBX 格式的文件。', 'error')
            return jsonify({'success': False, 'error': '不支持的文件格式'})

    return render_template('mesh_repair.html',
                           sidebar_items=items,
                           uploaded_files=uploaded_files)


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """提供上传的文件"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/get-mesh-data/<file_id>')
def get_mesh_data(file_id):
    """获取mesh文件数据用于可视化"""
    if file_id not in uploaded_files:
        return jsonify({'success': False, 'error': '文件不存在'})

    file_info = uploaded_files[file_id]

    # 在实际应用中，这里应该解析mesh文件并返回顶点、面片等数据
    # 现在返回模拟数据
    import random
    mesh_data = {
        'vertices': file_info.get('file_info', {}).get('vertices'),
        'faces': file_info.get('file_info', {}).get('faces'),
        'file_url': f"/uploads/{file_info['saved_name']}",
        'filename': file_info['original_name'],
        'format': file_info.get('file_info', {}).get('format', file_info['saved_name'].split('.')[-1].upper())
    }

    return jsonify({
        'success': True,
        'mesh_data': mesh_data
    })


@app.route('/analyze-mesh/<file_id>')
def analyze_mesh(file_id):
    """分析mesh文件"""
    if file_id not in uploaded_files:
        return jsonify({'success': False, 'error': '文件不存在'})

    file_info = uploaded_files[file_id]
    mesh = trimesh.load_mesh(file_info['filepath'])
    hd = HoleDetector(mesh)
    hole_loops = hd.detect_holes_2()

    # 返回分析结果（模拟数据）
    analysis_result = {
        'holes': len(hole_loops),
        'line_num': len(hd.boundary_edges)
    }

    return jsonify({
        'success': True,
        'analysis': analysis_result
    })


@app.route('/repair-mesh/<file_id>', methods=['POST'])
def repair_mesh(file_id):
    """修复mesh文件"""
    if file_id not in uploaded_files:
        return jsonify({'success': False, 'error': '文件不存在'})

    # 获取修复参数
    repair_options = request.json.get('options', {})

    file_info = uploaded_files[file_id]
    input_filepath = file_info['filepath']

    try:
        repaired_file_id = str(uuid.uuid4())
        repaired_filename = f"repaired_{file_info['original_name']}"
        repaired_filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"{repaired_file_id}.obj")

        # 调用实际的修复方法
        mesh = trimesh.load_mesh(input_filepath)
        hd = HoleDetector(mesh)
        hole_loops = hd.detect_holes_2()
        repairer = HoleRepairer(mesh)
        repaired_mesh = repairer.repair_all_holes(hole_loops, method='planar')
        repaired_mesh.export(repaired_filepath)

        # 获取修复后文件的信息
        repaired_file_info = get_file_info(repaired_filepath)

        CD = calculate_chamfer_distance(mesh, repaired_mesh, 20000)
        print(CD)
        # 存储修复后文件的信息
        uploaded_files[repaired_file_id] = {
            'original_name': repaired_filename,
            'saved_name': f"{repaired_file_id}.obj",
            'filepath': repaired_filepath,
            'file_info': repaired_file_info,
            'upload_time': '刚刚',
            'is_repaired': True,  # 标记为修复后的文件
            'original_file_id': file_id,  # 记录原始文件ID
            'chamfer_distance': CD[0]
        }

        # 返回修复结果
        repair_result = {
            'holes_filled': repair_options.get('holes_filled', 3),
            'edges_fixed': repair_options.get('edges_fixed', 12),
            'intersections_resolved': repair_options.get('intersections_resolved', 2),
            'vertices_removed': repair_options.get('vertices_removed', 8),
            'faces_repaired': repair_options.get('faces_repaired', 5),
            'success': True,
            'repaired_file_id': repaired_file_id,
            'repaired_filename': repaired_filename,
            'chamfer_distance': CD[0]
        }

        return jsonify({
            'success': True,
            'result': repair_result
        })

    except Exception as e:
        print(f"修复过程出错: {e}")
        return jsonify({
            'success': False,
            'error': f'修复失败: {str(e)}'
        })


@app.route('/download-repaired-mesh/<file_id>')
def download_repaired_mesh(file_id):
    """下载修复后的mesh文件"""
    if file_id not in uploaded_files:
        flash('文件不存在', 'error')
        return redirect(url_for('mesh_repair'))

    file_info = uploaded_files[file_id]

    # 确保这是修复后的文件
    if not file_info.get('is_repaired', False):
        flash('这不是修复后的文件', 'error')
        return redirect(url_for('mesh_repair'))

    return send_file(
        file_info['filepath'],
        as_attachment=True,
        download_name=file_info['original_name']
    )

@app.route('/download-mesh/<file_id>')
def download_mesh(file_id):
    """下载修复后的mesh文件"""
    if file_id not in uploaded_files:
        flash('文件不存在', 'error')
        return redirect(url_for('mesh_repair'))

    file_info = uploaded_files[file_id]

    # 在实际应用中，这里应该返回修复后的文件
    # 现在暂时返回原始文件
    return send_file(
        file_info['filepath'],
        as_attachment=True,
        download_name=f"{file_info['original_name']}"
    )


@app.route('/delete-mesh/<file_id>')
def delete_mesh(file_id):
    """删除上传的mesh文件"""
    if file_id in uploaded_files:
        file_info = uploaded_files[file_id]
        try:
            os.remove(file_info['filepath'])
        except:
            pass
        del uploaded_files[file_id]
        flash('文件已删除', 'success')

    return redirect(url_for('mesh_repair'))


if __name__ == '__main__':
    app.run(debug=True)