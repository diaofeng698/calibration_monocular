# Femto Bolt 相机标定工程

本工程用于标定Femto Bolt深度相机的内参和外参（相对于汽车后轴中心）。

## 功能特性

- **内参标定**：使用棋盘格标定板获取相机内参矩阵和畸变系数
- **外参标定**：计算相机相对于汽车后轴中心的外参矩阵
- **数据采集**：支持RGB和深度图像采集
- **可视化**：支持静态和实时交互式3D可视化
  - 🆕 **实时3D显示**：鼠标旋转、缩放、平移查看相机位置
  - 🆕 **交互式操作**：键盘快捷键保存截图和重置视角
  - 🆕 **多相机对比**：同时显示多个相机位置
  - 🆕 **自动旋转动画**：360度全景展示

## 环境依赖

```bash
pip install -r requirements.txt
```

## 使用说明

### 1. 内参标定

```bash
# 采集标定图像
python scripts/capture_calibration_images.py --output data/intrinsic_calibration

# 运行内参标定
python scripts/calibrate_intrinsic.py --input data/intrinsic_calibration --output config/intrinsic.yaml
```

### 2. 外参标定

```bash
# 手动测量标定（需要物理测量）
python scripts/calibrate_extrinsic_manual.py --output config/extrinsic.yaml

# 或使用标定板自动标定
python scripts/calibrate_extrinsic_auto.py --intrinsic config/intrinsic.yaml --output config/extrinsic.yaml --image data/extrinsic_calibration/frame_1770600232644000053.png --board-position 1.07 0.185 1.01
```

### 3. 验证标定结果

```bash
python scripts/verify_calibration.py --intrinsic config/intrinsic.yaml --extrinsic config/extrinsic.yaml
```

### 4. 🆕 实时3D可视化

```bash
# 基础用法 - 命令行指定位置
python scripts/view_3d_interactive.py \
    --position 1.5 0.0 1.8 \
    --orientation 0.0 -10.0 0.0

# 使用已有外参文件
python scripts/view_3d_interactive.py --extrinsic config/extrinsic.yaml

# 测试多相机位置
python examples/test_interactive_3d.py

# 完整示例集
python examples/realtime_3d_examples.py
```

**交互操作**:
- 鼠标左键拖动: 旋转视图
- 鼠标右键拖动: 平移视图
- 鼠标滚轮: 缩放
- 按 `r` 键: 重置视角
- 按 `s` 键: 保存截图
- 按 `q` 键: 退出

详细使用指南请参考: [INTERACTIVE_3D_GUIDE.md](INTERACTIVE_3D_GUIDE.md)

## 目录结构

```
femto_bolt/
├── README.md
├── requirements.txt
├── config/                  # 标定参数配置
├── data/                    # 数据存储
├── scripts/                 # 标定脚本
│   ├── capture_calibration_images.py
│   ├── calibrate_intrinsic.py
│   ├── calibrate_extrinsic_manual.py
│   ├── calibrate_extrinsic_auto.py
│   └── verify_calibration.py
├── src/                     # 源代码
│   ├── camera/             # 相机接口
│   ├── calibration/        # 标定算法
│   └── utils/              # 工具函数
└── notebooks/              # Jupyter notebooks示例
```

## 标定流程说明

### 内参标定
1. 打印棋盘格标定板（推荐9x6，方格大小25mm）
2. 从不同角度和距离采集20-30张图像
3. 运行标定算法获取内参矩阵K和畸变系数

### 外参标定
两种方法：

**方法1：手动测量（推荐用于固定安装）**
- 测量相机光心相对于后轴中心的位置(x, y, z)
- 测量相机的旋转角度（roll, pitch, yaw）
- 直接生成外参矩阵

**方法2：标定板自动标定**
- 将标定板放置在后轴中心已知位置
- 拍摄标定板图像
- 通过PnP算法计算相机位姿

## 坐标系定义

- **车辆坐标系**：原点在后轴中心，X轴向前，Y轴向左，Z轴向上
- **相机坐标系**：原点在相机光心，Z轴向前（光轴方向），X轴向右，Y轴向下

## 输出格式

标定结果保存为YAML文件：

```yaml
intrinsic:
  camera_matrix: [[fx, 0, cx], [0, fy, cy], [0, 0, 1]]
  distortion_coeffs: [k1, k2, p1, p2, k3]
  image_width: 640
  image_height: 480

extrinsic:
  rotation_matrix: [[r11, r12, r13], [r21, r22, r23], [r31, r32, r33]]
  translation_vector: [tx, ty, tz]
  # 相机在车辆坐标系中的位置和姿态
```
