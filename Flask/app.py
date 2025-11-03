from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for, send_from_directory
import os
import uuid
from werkzeug.utils import secure_filename
import tempfile
import shutil

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

        # 这里可以添加更详细的mesh文件解析逻辑
        # 目前返回模拟数据
        import random
        return {
            'vertices': random.randint(1000, 100000),
            'faces': random.randint(2000, 200000),
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
        'vertices': file_info.get('file_info', {}).get('vertices', random.randint(1000, 100000)),
        'faces': file_info.get('file_info', {}).get('faces', random.randint(2000, 200000)),
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

    # 模拟分析过程
    import time
    time.sleep(2)  # 模拟处理时间

    # 返回分析结果（模拟数据）
    analysis_result = {
        'holes': 3,
        'non_manifold_edges': 12,
        'self_intersections': 2,
        'isolated_vertices': 8,
        'degenerate_faces': 5
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

    # 模拟修复过程
    import time
    time.sleep(3)  # 模拟修复时间

    # 返回修复结果（模拟数据）
    repair_result = {
        'holes_filled': 3,
        'edges_fixed': 12,
        'intersections_resolved': 2,
        'vertices_removed': 8,
        'faces_repaired': 5,
        'success': True
    }

    return jsonify({
        'success': True,
        'result': repair_result
    })


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
        download_name=f"repaired_{file_info['original_name']}"
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