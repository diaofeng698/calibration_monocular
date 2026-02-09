# 实时3D可视化 - 快速参考

## 快速开始

### 方式1: 命令行指定位置（最简单）
```bash
python scripts/view_3d_interactive.py \
    --position 1.5 0.0 1.8 \
    --orientation 0.0 -10.0 0.0
```

### 方式2: 使用外参文件
```bash
python scripts/view_3d_interactive.py \
    --extrinsic config/extrinsic.yaml
```

### 方式3: 多相机测试
```bash
python examples/test_interactive_3d.py
```

---

## 交互操作

| 操作             | 功能         |
| ---------------- | ------------ |
| **鼠标左键拖动** | 旋转3D视图   |
| **鼠标右键拖动** | 平移3D视图   |
| **鼠标滚轮**     | 缩放视图     |
| **按 `r` 键**    | 重置视角     |
| **按 `s` 键**    | 保存当前截图 |
| **按 `q` 键**    | 退出程序     |

---

## 常用参数

```bash
python scripts/view_3d_interactive.py \
    --position X Y Z              # 相机位置 (米)
    --orientation ROLL PITCH YAW  # 相机姿态 (度)
    --car-length 4.0              # 车辆长度
    --car-width 2.0               # 车辆宽度
    --hide-camera-frame           # 隐藏相机坐标系
    --animate                     # 自动旋转动画
```

---

## 示例

### 前置中央相机
```bash
python scripts/view_3d_interactive.py \
    --position 2.0 0.0 1.5 \
    --orientation 0.0 -15.0 0.0
```

### 前置左侧相机
```bash
python scripts/view_3d_interactive.py \
    --position 1.8 0.8 1.5 \
    --orientation 0.0 -15.0 10.0
```

### 后置相机
```bash
python scripts/view_3d_interactive.py \
    --position -0.5 0.0 2.0 \
    --orientation 0.0 -20.0 180.0
```

### SUV大车
```bash
python scripts/view_3d_interactive.py \
    --position 2.5 0.0 1.9 \
    --orientation 0.0 -12.0 0.0 \
    --car-length 5.0 \
    --car-width 2.2
```

### 自动旋转演示
```bash
python scripts/view_3d_interactive.py \
    --extrinsic config/extrinsic.yaml \
    --animate
```

---

## Python代码使用

```python
import sys
sys.path.insert(0, 'scripts')
from view_3d_interactive import plot_camera_pose_3d_interactive
from src.calibration import ExtrinsicCalibration

import matplotlib
matplotlib.use('TkAgg')  # 设置GUI后端

# 创建外参
calibrator = ExtrinsicCalibration()
extrinsic = calibrator.from_manual_measurement(
    position=(1.5, 0.0, 1.8),
    orientation=(0.0, -10.0, 0.0),
    angle_unit='degree'
)

# 显示交互式3D
plot_camera_pose_3d_interactive(
    extrinsic_data=extrinsic,
    show_camera_frame=True,
    car_length=4.0,
    car_width=2.0,
    enable_animation=False
)
```

---

## 故障排查

### 问题: "No GUI backend available"
**解决**:
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# 或
pip install PyQt5
```

### 问题: SSH远程无法显示
**解决**:
```bash
# 方案1: X11转发
ssh -X user@server

# 方案2: 本地运行
scp user@server:/path/to/config/extrinsic.yaml .
python scripts/view_3d_interactive.py --extrinsic extrinsic.yaml
```

### 问题: 图形窗口太小/太大
**解决**: 修改 `view_3d_interactive.py` 第38行
```python
fig = plt.figure(figsize=(14, 10))  # 调整尺寸
```

---

## 相关文档

- 详细指南: [INTERACTIVE_3D_GUIDE.md](INTERACTIVE_3D_GUIDE.md)
- 实现说明: [REALTIME_3D_IMPLEMENTATION.md](REALTIME_3D_IMPLEMENTATION.md)
- 主文档: [README.md](README.md)

---

## 快速测试

```bash
# 测试环境
python test_interactive_3d.py

# 预期输出:
# ✓ 已使用GUI后端: TkAgg
# ✓ 所有测试通过！
```

---

**提示**: 在交互式3D窗口中，可以自由旋转查看各个角度的相机位置！

**版本**: 1.0 | **更新**: 2024-01-xx
