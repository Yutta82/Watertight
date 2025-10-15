from flask import Flask, render_template

app = Flask(__name__)

# 简化的侧边栏项目
sidebar_items = [
    {"name": "首页", "icon": "🏠", "url": "/", "active": True},
    {"name": "Mesh可视化", "icon": "🔍", "url": "/mesh-visualization", "active": False},
    {"name": "Mesh修补", "icon": "🔧", "url": "/mesh-repair", "active": False}
]

# Mesh数据示例
mesh_examples = [
    {"name": "立方体", "vertices": 8, "faces": 6, "file_size": "2.3KB"},
    {"name": "球体", "vertices": 642, "faces": 1280, "file_size": "45.2KB"},
    {"name": "斯坦福兔子", "vertices": 35947, "faces": 69451, "file_size": "3.2MB"},
    {"name": "龙模型", "vertices": 437645, "faces": 871414, "file_size": "24.7MB"}
]

@app.route('/')
def index():
    # 设置首页为激活状态
    items = sidebar_items.copy()
    items[0]["active"] = True
    items[1]["active"] = False
    items[2]["active"] = False
    return render_template('index.html',
                         sidebar_items=items,
                         mesh_examples=mesh_examples)

@app.route('/mesh-visualization')
def mesh_visualization():
    items = sidebar_items.copy()
    items[0]["active"] = False
    items[1]["active"] = True
    items[2]["active"] = False
    return render_template('mesh_visualization.html', sidebar_items=items)

@app.route('/mesh-repair')
def mesh_repair():
    items = sidebar_items.copy()
    items[0]["active"] = False
    items[1]["active"] = False
    items[2]["active"] = True
    return render_template('mesh_repair.html', sidebar_items=items)

if __name__ == '__main__':
    app.run(debug=True)