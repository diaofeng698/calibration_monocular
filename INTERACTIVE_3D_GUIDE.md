# 实时3D可视化使用指南

本项目支持**交互式实时3D可视化**功能，可以用鼠标旋转、缩放、平移查看相机在车辆坐标系中的位置。

## 目录
- [功能特性](#功能特性)
- [环境要求](#环境要求)
- [使用方法](#使用方法)
- [操作说明](#操作说明)
- [常见问题](#常见问题)

---

## 功能特性

✨ **交互式3D可视化**
- 🖱️ 鼠标旋转、缩放、平移
- 📸 保存当前视角截图
- 🎬 可选自动旋转动画
- 🎨 专业级渲染效果

✨ **多种使用方式**
- 从YAML文件加载外参
- 命令行直接指定位置姿态
- 同时显示多个相机位置

✨ **键盘快捷键**
- `r`: 重置视角
- `s`: 保存图像
- `q`: 退出程序

---

## 环境要求

### 1. Python环境
需要Python 3.7+，以及以下包：
```bash
pip install numpy matplotlib opencv-python pyyaml scipy transforms3d
```

### 2. GUI后端（重要！）

实时3D显示需要matplotlib的GUI后端。支持以下后端：

#### **选项1: TkAgg（推荐）**
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# CentOS/RHEL
sudo yum install python3-tkinter

# macOS（通常已内置）
# 无需额外安装

# Windows（通常已内置）
# 无需额外安装
```

#### **选项2: Qt5Agg**
```bash
pip install PyQt5
```

#### **选项3: 设置环境变量**
```bash
# 在运行前设置
export MPLBACKEND=TkAgg

# 或者
export MPLBACKEND=Qt5Agg
```

#### **检查当前后端**
```python
import matplotlib
print(matplotlib.get_backend())  # 应该输出 'TkAgg' 或 'Qt5Agg'，而不是 'Agg'
```

---

## 使用方法

### 方法1: 使用已有的外参文件

```bash
# 基础用法
python scripts/view_3d_interactive.py --extrinsic config/extrinsic.yaml

# 隐藏相机坐标系
python scripts/view_3d_interactive.py --extrinsic config/extrinsic.yaml --hide-camera-frame

# 自定义车辆尺寸
python scripts/view_3d_interactive.py --extrinsic config/extrinsic.yaml \
    --car-length 5.0 --car-width 2.2

# 启用自动旋转动画
python scripts/view_3d_interactive.py --extrinsic config/extrinsic.yaml --animate
```

### 方法2: 命令行直接指定位置

```bash
# 前置中央相机
python scripts/view_3d_interactive.py \
    --position 2.0 0.0 1.5 \
    --orientation 0.0 -15.0 0.0

# 前置左侧相机
python scripts/view_3d_interactive.py \
    --position 1.8 0.8 1.5 \
    --orientation 0.0 -15.0 10.0

# 后置相机
python scripts/view_3d_interactive.py \
    --position -0.5 0.0 2.0 \
    --orientation 0.0 -20.0 180.0
```

### 方法3: 测试多相机位置

```bash
# 同时显示4个相机位置
python examples/test_interactive_3d.py
```

### 方法4: 在Python代码中使用

```python
from src.calibration import ExtrinsicCalibration
import matplotlib
matplotlib.use('TkAgg')  # 设置GUI后端

from scripts.view_3d_interactive import plot_camera_pose_3d_interactive

# 创建外参
calibrator = ExtrinsicCalibration()
extrinsic_data = calibrator.from_manual_measurement(
    position=(1.5, 0.0, 1.8),
    orientation=(0.0, -10.0, 0.0),
    angle_unit='degree'
)

# 显示交互式3D图形
plot_camera_pose_3d_interactive(
    extrinsic_data=extrinsic_data,
    show_camera_frame=True,
    car_length=4.0,
    car_width=2.0,
    enable_animation=False
)
```

---

## 操作说明

### 鼠标操作
| 操作         | 功能       |
| ------------ | ---------- |
| **左键拖动** | 旋转3D视图 |
| **右键拖动** | 平移3D视图 |
| **滚轮**     | 缩放视图   |

### 键盘快捷键
| 按键 | 功能                           |
| ---- | ------------------------------ |
| `r`  | 重置视角（仰角25°，方位角45°） |
| `s`  | 保存当前视角为PNG图片          |
| `q`  | 关闭窗口并退出                 |

### 自动旋转动画
启用 `--animate` 参数后：
- 3D视图会自动旋转（360°循环）
- 仍可使用鼠标手动控制
- 按 `q` 键停止并退出

---

## 常见问题

### Q1: 提示"No GUI backend available"

**原因**: matplotlib使用的是Agg后端（非GUI）

**解决方案**:
```bash
# 方法1: 安装tkinter
sudo apt-get install python3-tk

# 方法2: 安装PyQt5
pip install PyQt5

# 方法3: 设置环境变量
export MPLBACKEND=TkAgg
python scripts/view_3d_interactive.py ...
```

### Q2: 图形窗口无法显示

**可能原因**:
- SSH连接到远程服务器，没有X11转发
- Docker容器中运行，没有显示设备

**解决方案**:

#### 本地机器运行
最简单的方式是在本地机器上运行：
```bash
# 1. 将外参文件复制到本地
scp user@server:/path/to/config/extrinsic.yaml .

# 2. 在本地运行
python scripts/view_3d_interactive.py --extrinsic extrinsic.yaml
```

#### SSH + X11转发
```bash
# 1. 在本地安装X11服务器
# Windows: 安装 VcXsrv 或 Xming
# macOS: 安装 XQuartz
# Linux: 通常已安装

# 2. SSH连接时启用X11转发
ssh -X user@server

# 3. 测试X11
xeyes  # 如果能看到眼睛，说明X11工作正常

# 4. 运行脚本
python scripts/view_3d_interactive.py ...
```

#### 保存为图像文件（替代方案）
如果实在无法使用GUI，可以使用静态可视化：
```python
from src.utils.visualization import plot_camera_pose_3d

# 保存为PNG文件（使用Agg后端）
plot_camera_pose_3d(
    extrinsic_data=extrinsic_data,
    save_path='output/camera_pose.png'
)
```

### Q3: 如何同时显示多个相机？

使用 `test_interactive_3d.py` 示例：
```bash
python examples/test_interactive_3d.py
```

或者修改代码，在循环中添加相机：
```python
for cam_config in camera_list:
    # 绘制每个相机的位置和朝向
    ax.scatter(...)
```

### Q4: 如何更改视角和渲染效果？

修改 `plot_camera_pose_3d_interactive()` 函数中的参数：

```python
# 初始视角
ax.view_init(elev=30, azim=60)  # 仰角30°，方位角60°

# 坐标轴范围
ax.set_xlim([xmin, xmax])
ax.set_ylim([ymin, ymax])
ax.set_zlim([zmin, zmax])

# 标记大小
ax.scatter(..., s=500)  # 相机标记更大

# 线条粗细
ax.quiver(..., linewidth=3.5)  # 坐标轴更粗
```

### Q5: 如何导出高分辨率图像？

按 `s` 键会以150 DPI保存。如需更高分辨率：

```python
# 在代码中修改
plt.savefig('output.png', dpi=300, bbox_inches='tight')

# 或修改 on_key() 函数中的 DPI 值
```

### Q6: 动画卡顿怎么办？

```python
# 降低动画帧率
anim = animation.FuncAnimation(
    fig, animate, 
    frames=180,    # 帧数
    interval=100,  # 增大间隔（毫秒）
    blit=False
)
```

---

## 完整命令行参数

```
usage: view_3d_interactive.py [-h] [--extrinsic EXTRINSIC]
                              [--position x y z]
                              [--orientation roll pitch yaw]
                              [--car-length METERS]
                              [--car-width METERS]
                              [--hide-camera-frame]
                              [--animate]

参数说明:
  --extrinsic EXTRINSIC       外参文件路径（YAML格式）
  --position x y z            相机位置（米），相对于后轴中心
  --orientation roll pitch yaw 相机姿态（度），欧拉角
  --car-length METERS         车辆长度（默认4.0米）
  --car-width METERS          车辆宽度（默认2.0米）
  --hide-camera-frame         不显示相机自身坐标系
  --animate                   启用自动旋转动画
```

---

## 示例效果

### 前置中央相机
```bash
python scripts/view_3d_interactive.py \
    --position 2.0 0.0 1.5 \
    --orientation 0.0 -15.0 0.0
```

效果：
- 相机位于车辆前方2米，高度1.5米
- 俯仰角-15°（向下看）
- 可旋转查看360°全景

### 多相机阵列
```bash
python examples/test_interactive_3d.py
```

效果：
- 同时显示4个相机位置
- 不同颜色区分
- 显示每个相机的光轴方向

---

## 技术说明

### 坐标系定义

**车辆坐标系** (后轴中心为原点):
- X轴: 车辆前进方向（红色）
- Y轴: 车辆左侧方向（绿色）
- Z轴: 车辆向上方向（蓝色）

**相机坐标系**:
- X轴: 图像右侧方向（浅红色虚线）
- Y轴: 图像下侧方向（浅绿色虚线）
- Z轴: 光轴方向（浅蓝色虚线）

### 文件输出格式

按 `s` 键保存的文件：
- 文件名: `camera_pose_3d_YYYYMMDD_HHMMSS.png`
- 格式: PNG
- 分辨率: 150 DPI（可修改）
- 位置: 当前工作目录

---

## 高级用法

### 自定义视角预设

创建一个配置文件 `view_presets.yaml`:
```yaml
views:
  top:
    elev: 90
    azim: 0
  front:
    elev: 0
    azim: 0
  side:
    elev: 0
    azim: 90
  isometric:
    elev: 25
    azim: 45
```

在代码中加载：
```python
import yaml

with open('view_presets.yaml') as f:
    presets = yaml.safe_load(f)

# 使用预设视角
ax.view_init(
    elev=presets['views']['isometric']['elev'],
    azim=presets['views']['isometric']['azim']
)
```

### 添加更多交互功能

可以扩展 `on_key()` 函数：
```python
def on_key(event):
    if event.key == 't':
        # 俯视图
        ax.view_init(elev=90, azim=0)
    elif event.key == 'f':
        # 前视图
        ax.view_init(elev=0, azim=0)
    elif event.key == 'l':
        # 左视图
        ax.view_init(elev=0, azim=90)
    # ... 更多快捷键
```

---

## 相关文件

| 文件                                | 说明                      |
| ----------------------------------- | ------------------------- |
| `scripts/view_3d_interactive.py`    | 交互式3D可视化主脚本      |
| `examples/test_interactive_3d.py`   | 多相机位置测试示例        |
| `src/utils/visualization.py`        | 静态可视化工具（Agg后端） |
| `examples/test_3d_visualization.py` | 静态3D测试                |

---

## 对比: 静态 vs 交互式

| 特性         | 静态模式         | 交互式模式       |
| ------------ | ---------------- | ---------------- |
| **后端**     | Agg              | TkAgg/Qt5Agg     |
| **鼠标交互** | ❌                | ✅ 旋转/缩放/平移 |
| **实时预览** | ❌                | ✅ 实时渲染       |
| **保存图片** | ✅ 自动保存       | ✅ 按's'键保存    |
| **远程使用** | ✅ 支持           | ⚠️ 需X11转发      |
| **Docker**   | ✅ 支持           | ❌ 通常不支持     |
| **使用场景** | 批量处理、自动化 | 探索性分析、演示 |

---

## 许可证

本项目遵循MIT许可证。

---

## 联系方式

如有问题或建议，请提交Issue。

---

**更新日期**: 2024-01-xx
**版本**: 1.0
