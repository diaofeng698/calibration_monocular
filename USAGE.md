# Femto Bolt 相机标定工程使用指南

## 快速开始

### 1. 安装依赖

```bash
cd /data/fdiao/learning/BEV/femto_bolt
pip install -r requirements.txt
```

### 2. 准备棋盘格标定板

打印一个棋盘格标定板：
- 推荐尺寸：9×6（内角点数量）
- 方格大小：25mm × 25mm
- 打印在硬质板上，保持平整

你可以使用OpenCV提供的标定板生成工具，或从这里下载：
https://github.com/opencv/opencv/blob/master/doc/pattern.png

### 3. 内参标定

#### 步骤1：采集标定图像

```bash
python scripts/capture_calibration_images.py --output data/intrinsic_calibration
```

- 从不同角度和距离拍摄20-30张包含棋盘格的图像
- 确保棋盘格完全可见且清晰
- 按空格键保存图像，按'q'退出

#### 步骤2：运行标定

```bash
python scripts/calibrate_intrinsic.py \
    --input data/intrinsic_calibration \
    --output config/intrinsic.yaml \
    --checkerboard 9 6 \
    --square-size 0.025
```

参数说明：
- `--input`: 标定图像所在文件夹
- `--output`: 输出的内参文件
- `--checkerboard`: 棋盘格内角点数量（列 行）
- `--square-size`: 方格尺寸（米）

### 4. 外参标定

有两种方法：

#### 方法A：手动测量（推荐）

手动测量相机相对于后轴中心的位置和姿态：

```bash
python scripts/calibrate_extrinsic_manual.py \
    --position 1.5 0.0 1.8 \
    --orientation 0.0 -10.0 0.0 \
    --output config/extrinsic.yaml
```

或使用交互式输入：

```bash
python scripts/calibrate_extrinsic_manual.py --interactive
```

参数说明：
- `--position x y z`: 相机位置（米）
  - x: 向前距离（正值表示在后轴前方）
  - y: 向左距离（正值表示在车辆左侧）
  - z: 向上高度（正值表示在地面上方）
- `--orientation roll pitch yaw`: 相机姿态（度）
  - roll: 绕X轴旋转（左右倾斜）
  - pitch: 绕Y轴旋转（俯仰，负值向下看）
  - yaw: 绕Z轴旋转（偏航）

#### 方法B：标定板自动标定

1. 将标定板放置在车辆坐标系中已知位置
2. 拍摄一张包含标定板的图像
3. 运行标定：

```bash
python scripts/calibrate_extrinsic_auto.py \
    --intrinsic config/intrinsic.yaml \
    --image data/board_image.jpg \
    --board-position 1.0 0.0 0.0 \
    --board-orientation 0.0 0.0 0.0 \
    --output config/extrinsic.yaml
```

### 5. 验证标定结果

```bash
python scripts/verify_calibration.py \
    --intrinsic config/intrinsic.yaml \
    --extrinsic config/extrinsic.yaml \
    --live
```

## 使用示例

### 示例1：查看标定结果

```bash
cd examples
python calibration_example.py
# 选择选项5
```

### 示例2：实时使用标定参数

```bash
cd examples
python realtime_usage.py
```

这个示例展示了如何：
- 使用内参去除图像畸变
- 将像素坐标转换为相机坐标
- 将相机坐标转换为车辆坐标

## 测量技巧

### 测量相机位置

1. **X轴（前后）**：
   - 测量相机光心到后轴中心的水平前后距离
   - 向前为正，向后为负

2. **Y轴（左右）**：
   - 测量相机光心到车辆中心线的左右距离
   - 向左为正，向右为负

3. **Z轴（高度）**：
   - 测量相机光心到地面的垂直高度
   - 向上为正

### 测量相机姿态

1. **Pitch（俯仰角）**：
   - 使用水平仪或角度仪测量相机向下倾斜的角度
   - 向下看为负，向上看为正
   - 例如：向下倾斜10度，则pitch = -10

2. **Yaw（偏航角）**：
   - 测量相机相对于车辆前进方向的偏转角度
   - 向左偏转为正，向右为负

3. **Roll（横滚角）**：
   - 测量相机的左右倾斜角度
   - 通常应该为0（保持水平）

## 常见问题

### Q1: 标定板检测失败
- 确保标定板完全可见
- 检查光照是否充足
- 确认棋盘格参数是否正确
- 尝试调整相机焦距使图像更清晰

### Q2: 标定精度不够
- 增加标定图像数量（推荐30张以上）
- 确保图像覆盖整个视野
- 包含不同距离和角度的图像
- 检查标定板是否平整

### Q3: 相机无法启动
- 检查是否正确安装pyrealsense2
- 确认相机已正确连接
- 程序会在无法连接相机时使用模拟模式

### Q4: 如何验证外参是否正确
- 使用verify_calibration.py脚本
- 检查3D可视化中相机位置是否合理
- 测试坐标转换结果是否符合预期

## 进阶使用

### 在代码中使用标定结果

```python
from src.utils import load_calibration
from src.calibration import ExtrinsicCalibration
import numpy as np

# 加载内参
intrinsic = load_calibration('config/intrinsic.yaml')
camera_matrix = np.array(intrinsic['camera_matrix'])
dist_coeffs = np.array(intrinsic['distortion_coeffs'])

# 加载外参
extrinsic = load_calibration('config/extrinsic.yaml')
calib = ExtrinsicCalibration()
calib.load_from_dict(extrinsic)

# 坐标转换
point_camera = np.array([0, 0, 2.0])  # 相机前方2米
point_vehicle = calib.transform_point_to_vehicle(point_camera)
print(f"车辆坐标: {point_vehicle}")
```

## 参考资料

- OpenCV Camera Calibration: https://docs.opencv.org/master/dc/dbb/tutorial_py_calibration.html
- Camera Calibration and 3D Reconstruction: https://docs.opencv.org/master/d9/d0c/group__calib3d.html

## 技术支持

如有问题，请检查：
1. requirements.txt中的依赖是否正确安装
2. Python版本是否为3.7+
3. OpenCV版本是否为4.5+
