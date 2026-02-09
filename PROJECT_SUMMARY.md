# Femto Bolt 相机标定工程 - 项目总结

## ✅ 已完成的功能

### 1. 完整的项目结构
```
femto_bolt/
├── README.md                    # 项目说明
├── USAGE.md                     # 详细使用指南
├── QUICKSTART.sh                # 快速开始脚本
├── requirements.txt             # Python依赖
├── test_installation.py         # 安装测试脚本
├── config/                      # 配置文件目录
│   ├── intrinsic_example.yaml   # 内参示例
│   └── extrinsic_example.yaml   # 外参示例
├── data/                        # 数据存储
│   ├── intrinsic_calibration/   # 内参标定图像
│   └── extrinsic_calibration/   # 外参标定图像
├── src/                         # 源代码
│   ├── camera/                  # 相机接口
│   │   ├── femto_bolt.py       # Femto Bolt相机类
│   │   └── __init__.py
│   ├── calibration/            # 标定算法
│   │   ├── intrinsic_calibration.py    # 内参标定
│   │   ├── extrinsic_calibration.py    # 外参标定
│   │   └── __init__.py
│   └── utils/                  # 工具函数
│       ├── file_utils.py       # 文件操作
│       ├── visualization.py     # 可视化
│       └── __init__.py
├── scripts/                     # 标定脚本
│   ├── capture_calibration_images.py      # 采集标定图像
│   ├── calibrate_intrinsic.py             # 内参标定
│   ├── calibrate_extrinsic_manual.py      # 手动外参标定
│   ├── calibrate_extrinsic_auto.py        # 自动外参标定
│   └── verify_calibration.py              # 验证标定结果
└── examples/                    # 使用示例
    ├── calibration_example.py   # 标定流程示例
    └── realtime_usage.py        # 实时使用示例
```

### 2. 核心功能模块

#### 2.1 相机接口 (src/camera/femto_bolt.py)
- ✅ Femto Bolt相机初始化和配置
- ✅ RGB和深度图像采集
- ✅ 相机内参读取
- ✅ 模拟模式支持（无相机时测试）
- ✅ 上下文管理器支持

#### 2.2 内参标定 (src/calibration/intrinsic_calibration.py)
- ✅ 棋盘格角点检测
- ✅ 亚像素精确化
- ✅ 相机内参矩阵计算
- ✅ 畸变系数估计
- ✅ 重投影误差计算
- ✅ 图像去畸变
- ✅ 批量图像处理

#### 2.3 外参标定 (src/calibration/extrinsic_calibration.py)
- ✅ 手动测量方法（通过物理测量设置外参）
- ✅ PnP自动标定方法
- ✅ 棋盘格自动标定
- ✅ 坐标系变换（相机 ↔ 车辆）
- ✅ 欧拉角和旋转矩阵转换
- ✅ 4x4变换矩阵构建

#### 2.4 工具函数 (src/utils/)
- ✅ YAML格式标定结果保存/加载
- ✅ JSON格式支持
- ✅ 标定结果可视化
- ✅ 3D位姿可视化
- ✅ 坐标轴绘制
- ✅ 去畸变效果对比

### 3. 标定脚本

#### 3.1 图像采集 (scripts/capture_calibration_images.py)
- ✅ 实时相机预览
- ✅ 空格键保存图像
- ✅ 图像计数显示
- ✅ 采集进度提示

#### 3.2 内参标定 (scripts/calibrate_intrinsic.py)
- ✅ 批量图像处理
- ✅ 角点检测可视化
- ✅ 标定参数计算
- ✅ 误差分析
- ✅ 去畸变效果展示

#### 3.3 外参标定 - 手动 (scripts/calibrate_extrinsic_manual.py)
- ✅ 命令行参数输入
- ✅ 交互式参数输入
- ✅ 坐标系说明
- ✅ 3D可视化
- ✅ 坐标变换验证

#### 3.4 外参标定 - 自动 (scripts/calibrate_extrinsic_auto.py)
- ✅ 标定板检测
- ✅ PnP位姿估计
- ✅ 标定板位置配置
- ✅ 检测结果可视化

#### 3.5 标定验证 (scripts/verify_calibration.py)
- ✅ 标定结果加载和显示
- ✅ 去畸变实时测试
- ✅ 坐标变换验证
- ✅ 3D位姿可视化

### 4. 使用示例

#### 4.1 标定流程示例 (examples/calibration_example.py)
- ✅ 内参标定完整流程
- ✅ 手动外参标定流程
- ✅ 自动外参标定流程
- ✅ 标定结果使用示例
- ✅ 交互式菜单

#### 4.2 实时使用示例 (examples/realtime_usage.py)
- ✅ 标定参数加载
- ✅ 实时图像去畸变
- ✅ 像素到车辆坐标转换
- ✅ 交互式点选
- ✅ 实时坐标显示

### 5. 文档和配置

- ✅ README.md - 项目概述
- ✅ USAGE.md - 详细使用说明
- ✅ QUICKSTART.sh - 快速开始脚本
- ✅ requirements.txt - 依赖清单
- ✅ 示例配置文件
- ✅ .gitignore 配置

### 6. 测试和验证

- ✅ test_installation.py - 完整的安装测试
  - 文件结构检查
  - 依赖库检查
  - 模块导入检查
  - 基本功能验证

## 🎯 主要特性

### 标定方法
1. **内参标定**
   - 使用OpenCV棋盘格标定法
   - 支持多图像优化
   - 自动亚像素精确化
   - 完整的误差分析

2. **外参标定**
   - 方法1：手动测量（推荐用于固定安装）
   - 方法2：标定板自动标定（基于PnP）
   - 灵活的坐标系定义
   - 完整的变换矩阵

### 坐标系定义
- **车辆坐标系**：原点在后轴中心
  - X轴：向前为正
  - Y轴：向左为正
  - Z轴：向上为正

- **相机坐标系**：原点在相机光心
  - Z轴：向前（光轴方向）
  - X轴：向右
  - Y轴：向下

### 输出格式
标定结果保存为YAML文件，包含：
- 内参矩阵 (3x3)
- 畸变系数 (5维)
- 旋转矩阵 (3x3)
- 平移向量 (3维)
- 变换矩阵 (4x4)
- 欧拉角 (roll, pitch, yaw)

## 📋 使用流程

### 快速开始
```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 测试安装
python test_installation.py

# 3. 采集标定图像（20-30张）
python scripts/capture_calibration_images.py --output data/intrinsic_calibration

# 4. 内参标定
python scripts/calibrate_intrinsic.py \
    --input data/intrinsic_calibration \
    --output config/intrinsic.yaml

# 5. 外参标定（手动测量）
python scripts/calibrate_extrinsic_manual.py --interactive

# 6. 验证结果
python scripts/verify_calibration.py \
    --intrinsic config/intrinsic.yaml \
    --extrinsic config/extrinsic.yaml
```

## 🛠️ 技术栈

- **Python 3.7+**
- **OpenCV 4.5+** - 图像处理和标定
- **NumPy** - 数值计算
- **transforms3d** - 3D变换
- **PyYAML** - 配置文件
- **Matplotlib** - 可视化
- **pyrealsense2** - 相机SDK（可选）

## 📊 测试结果

所有核心功能已测试通过：
- ✅ 文件结构完整
- ✅ 所有依赖库正常导入
- ✅ 所有项目模块可用
- ✅ 基本功能正常工作
- ✅ 坐标变换准确

## 💡 应用场景

本工程适用于：
1. **自动驾驶** - 感知系统标定
2. **机器人** - 视觉定位
3. **BEV系统** - 鸟瞰图生成
4. **ADAS** - 辅助驾驶系统
5. **3D重建** - 点云处理

## 📝 注意事项

1. **内参标定**
   - 建议采集20-30张图像
   - 覆盖整个视野范围
   - 包含不同距离和角度
   - 确保标定板清晰可见

2. **外参标定**
   - 精确测量相机位置
   - 注意坐标系定义
   - 验证标定结果的合理性

3. **相机支持**
   - 已支持pyrealsense2接口
   - 无相机时可使用模拟模式
   - 可扩展支持其他相机

## 🔄 后续扩展方向

1. 支持更多相机型号
2. 添加在线标定功能
3. 实现自动标定优化
4. 增加标定精度评估
5. 支持多相机联合标定
6. 添加GUI界面
7. 集成到ROS系统

## 📚 参考资料

- [OpenCV Camera Calibration Tutorial](https://docs.opencv.org/master/dc/dbb/tutorial_py_calibration.html)
- [Camera Calibration and 3D Reconstruction](https://docs.opencv.org/master/d9/d0c/group__calib3d.html)
- [Zhang's Camera Calibration Method](https://www.microsoft.com/en-us/research/publication/a-flexible-new-technique-for-camera-calibration/)

## 👨‍💻 作者

创建于 2026年1月

## 📄 许可证

本项目仅供学习和研究使用。
