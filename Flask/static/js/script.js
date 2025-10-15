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

    // 模拟3D画布交互
    const meshCanvas = document.getElementById('meshCanvas');
    if (meshCanvas) {
        meshCanvas.addEventListener('click', function() {
            this.innerHTML = `
                <div class="text-center text-muted">
                    <div class="spinner-border text-primary mb-3" role="status">
                        <span class="visually-hidden">加载中...</span>
                    </div>
                    <h5>加载3D模型...</h5>
                    <p>正在初始化WebGL渲染器</p>
                </div>
            `;

            // 模拟加载过程
            setTimeout(() => {
                this.innerHTML = `
                    <div class="text-center text-success">
                        <i class="fas fa-check-circle fa-3x mb-3"></i>
                        <h5>模型加载成功！</h5>
                        <p>使用鼠标进行旋转、缩放操作</p>
                        <button class="btn btn-outline-primary mt-2" onclick="resetView()">
                            <i class="fas fa-rotate me-2"></i>重置视图
                        </button>
                    </div>
                `;
            }, 2000);
        });
    }

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