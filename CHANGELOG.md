# 更新日志

## 2026-01-27 - 3D可视化字体修复

### 问题
- 3D可视化中使用中文标签导致字体缺失警告
- DejaVu Sans字体不支持中文字符
- 大量"Glyph missing from font"警告信息

### 解决方案
将 `src/utils/visualization.py` 中的 `plot_camera_pose_3d()` 函数的所有中文标签改为英文：

#### 修改内容
```python
# 修改前（中文）
ax.quiver(..., label='X (前)')
ax.quiver(..., label='Y (左)')
ax.quiver(..., label='Z (上)')
ax.scatter(..., label='相机')
ax.plot(..., label='车辆轮廓')
ax.set_xlabel('X (前) [m]')
ax.set_ylabel('Y (左) [m]')
ax.set_zlabel('Z (上) [m]')
ax.set_title('相机在车辆坐标系中的位置')

# 修改后（英文）
ax.quiver(..., label='X (Forward)')
ax.quiver(..., label='Y (Left)')
ax.quiver(..., label='Z (Up)')
ax.scatter(..., label='Camera')
ax.plot(..., label='Vehicle Outline')
ax.set_xlabel('X (Forward) [m]')
ax.set_ylabel('Y (Left) [m]')
ax.set_zlabel('Z (Up) [m]')
ax.set_title('Camera Position in Vehicle Coordinate System')
```

### 影响范围
- ✅ `src/utils/visualization.py` - plot_camera_pose_3d函数
- ✅ `scripts/calibrate_extrinsic_manual.py` - 添加异常处理
- ✅ `scripts/calibrate_extrinsic_auto.py` - 添加异常处理

### 测试结果
✓ 无字体警告
✓ 3D可视化图像正常生成
✓ 标签清晰可读
✓ 输出文件大小: 270KB

### 额外优化
- 在两个标定脚本中添加了try-except异常处理
- 无GUI环境下会优雅地跳过3D可视化
- 保持其他功能正常运行

### 使用示例
```bash
# 手动外参标定（已测试）
python scripts/calibrate_extrinsic_manual.py \
    --position 1.5 0.0 1.8 \
    --orientation 0.0 -10.0 0.0 \
    --output config/extrinsic.yaml

# 输出: config/camera_pose_3d.png (无警告)
```

### 相关文件
- `src/utils/visualization.py` - 核心修改
- `scripts/calibrate_extrinsic_manual.py` - 异常处理
- `scripts/calibrate_extrinsic_auto.py` - 异常处理
- `config/camera_pose_3d.png` - 生成的可视化图像

### 注意事项
- 控制台输出（终端打印）保持中文，便于中文用户理解
- 仅图像标签使用英文，避免字体问题
- 文档保持中文，方便阅读和维护
