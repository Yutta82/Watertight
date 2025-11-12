// 侧边栏切换功能
document.addEventListener('DOMContentLoaded', function() {
    const sidebarToggle = document.querySelector('[data-bs-toggle="collapse"]');
    const sidebar = document.getElementById('sidebar');

    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.toggle('show');
        });
    }

    // 在移动端点击主内容区域关闭侧边栏
    document.querySelector('main').addEventListener('click', function() {
        if (window.innerWidth <= 768 && sidebar.classList.contains('show')) {
            sidebar.classList.remove('show');
        }
    });

    // 修复流程步骤交互
    const steps = document.querySelectorAll('.step');
    steps.forEach((step, index) => {
        step.addEventListener('click', function() {
            if (index < 2) { // 只允许点击前两步进行演示
                steps.forEach(s => s.classList.remove('active', 'completed'));
                for (let i = 0; i <= index; i++) {
                    steps[i].classList.add('completed');
                }
                steps[index].classList.add('active');
            }
        });
    });

    // 一键修复按钮
    const repairBtn = document.querySelector('.btn-success');
    if (repairBtn) {
        repairBtn.addEventListener('click', function() {
            const originalText = this.innerHTML;
            this.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>修复中...';
            this.disabled = true;

            setTimeout(() => {
                this.innerHTML = '<i class="fas fa-check me-2"></i>修复完成！';
                this.className = 'btn btn-success';

                // 更新问题计数
                const badges = document.querySelectorAll('.badge');
                badges.forEach(badge => {
                    badge.textContent = '0';
                    badge.className = 'badge bg-success rounded-pill';
                });

                // 前进到下一步
                setTimeout(() => {
                    steps.forEach(s => s.classList.remove('active', 'completed'));
                    for (let i = 0; i <= 2; i++) {
                        steps[i].classList.add('completed');
                    }
                    steps[2].classList.add('active');
                }, 1000);

            }, 3000);
        });
    }
});

// 重置视图函数
function resetView() {
    alert('视图已重置到初始位置');
}

// 文件上传模拟
function simulateFileUpload() {
    const uploadArea = document.querySelector('.card-body.text-center');
    if (uploadArea) {
        uploadArea.innerHTML = `
            <div class="text-center">
                <div class="spinner-border text-primary mb-3" role="status">
                    <span class="visually-hidden">上传中...</span>
                </div>
                <h5>文件上传中...</h5>
                <p>请不要关闭页面</p>
                <div class="progress mt-3">
                    <div class="progress-bar progress-bar-striped progress-bar-animated" style="width: 0%"></div>
                </div>
            </div>
        `;

        const progressBar = document.querySelector('.progress-bar');
        let width = 0;
        const interval = setInterval(() => {
            width += 5;
            progressBar.style.width = width + '%';
            if (width >= 100) {
                clearInterval(interval);
                setTimeout(() => {
                    uploadArea.innerHTML = `
                        <div class="text-center text-success">
                            <i class="fas fa-check-circle fa-3x mb-3"></i>
                            <h5>上传成功！</h5>
                            <p>文件已成功上传并准备进行分析</p>
                            <button class="btn btn-primary mt-2" onclick="analyzeMesh()">
                                <i class="fas fa-search me-2"></i>开始分析
                            </button>
                        </div>
                    `;
                }, 500);
            }
        }, 100);
    }
}

// 分析网格函数
function analyzeMesh() {
    alert('开始分析网格几何特征...');
}

// 修复mesh文件
function repairMesh() {
    if (!currentFileId) {
        alert('请先选择一个文件');
        return;
    }

    // 显示修复进度
    document.getElementById('repairControls').style.display = 'none';
    document.getElementById('repairProgress').style.display = 'block';

    // 获取修复选项
    const repairOptions = {
        hole_filling: document.getElementById('holeFilling').checked,
        self_intersection: document.getElementById('selfIntersection').checked,
        manifold_check: document.getElementById('manifoldCheck').checked,
        smoothing: document.getElementById('smoothing').checked,
        strength: parseInt(document.getElementById('repairStrength').value)
    };

    // 发送修复请求
    fetch(`/repair-mesh/${currentFileId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            options: repairOptions
        })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('repairProgress').style.display = 'none';
        document.getElementById('repairControls').style.display = 'block';

        if (data.success) {
            // 显示修复结果
            displayRepairResults(data.result);

            // 启用下载按钮
            const downloadButton = document.getElementById('downloadButton');
            downloadButton.disabled = false;
            downloadButton.onclick = function() {
                downloadRepairedMesh(data.result.repaired_file_id);
            };

            // 添加查看修复后模型的按钮
            addViewRepairedButton(data.result.repaired_file_id, data.result.repaired_filename);

            updateStep(4); // 进入结果验证步骤
        } else {
            alert('修复失败: ' + data.error);
        }
    })
    .catch(error => {
        document.getElementById('repairProgress').style.display = 'none';
        document.getElementById('repairControls').style.display = 'block';
        alert('修复过程中发生错误: ' + error.message);
    });
}

// 下载修复后的模型
function downloadRepairedMesh(fileId) {
    if (fileId) {
        window.open(`/download-repaired-mesh/${fileId}`, '_blank');
    } else {
        alert('没有可下载的修复文件');
    }
}

// 添加查看修复后模型的按钮
function addViewRepairedButton(fileId, filename) {
    const repairControls = document.getElementById('repairControls');

    // 移除已存在的查看按钮
    const existingViewButton = document.getElementById('viewRepairedButton');
    if (existingViewButton) {
        existingViewButton.remove();
    }

    // 添加新的查看按钮
    const viewButton = document.createElement('button');
    viewButton.id = 'viewRepairedButton';
    viewButton.className = 'btn btn-outline-info mt-2';
    viewButton.innerHTML = '<i class="fas fa-eye me-2"></i>查看修复后的模型';
    viewButton.onclick = function() {
        // 跳转到可视化页面并加载修复后的模型
        window.location.href = `/mesh-visualization?file=${fileId}`;
    };

    repairControls.appendChild(viewButton);
}

// 显示修复结果
function displayRepairResults(result) {
    const resultsHtml = `
        <div class="alert alert-success">
            <h6><i class="fas fa-check-circle me-2"></i>修复完成！</h6>
            <div class="small mt-2">
                <div>✓ 修复了 ${result.holes_filled} 个孔洞</div>
                <div>✓ 修复了 ${result.edges_fixed} 条非流形边</div>
                <div>✓ 解决了 ${result.intersections_resolved} 个自交问题</div>
                <div>✓ 移除了 ${result.vertices_removed} 个孤立顶点</div>
                <div>✓ 修复了 ${result.faces_repaired} 个退化面片</div>
                <div class="mt-2"><strong>修复后文件:</strong> ${result.repaired_filename}</div>
            </div>
        </div>
    `;

    // 在分析结果区域显示修复结果
    document.getElementById('analysisResults').innerHTML = resultsHtml;
}