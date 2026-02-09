# 快速开始脚本

## Linux/Mac
chmod +x scripts/*.py
chmod +x examples/*.py

## 完整标定流程

### 1. 安装依赖
pip install -r requirements.txt

### 2. 内参标定
# 采集图像（20-30张）
python scripts/capture_calibration_images.py --output data/intrinsic_calibration

# 运行标定
python scripts/calibrate_intrinsic.py \
    --input data/intrinsic_calibration \
    --output config/intrinsic.yaml

### 3. 外参标定（手动测量方式）
# 交互式输入
python scripts/calibrate_extrinsic_manual.py --interactive --output config/extrinsic.yaml

# 或直接指定参数（示例：相机在车辆上方1.8米，前方1.5米，向下倾斜10度）
python scripts/calibrate_extrinsic_manual.py \
    --position 1.5 0.0 1.8 \
    --orientation 0.0 -10.0 0.0 \
    --output config/extrinsic.yaml

### 4. 验证标定结果
python scripts/verify_calibration.py \
    --intrinsic config/intrinsic.yaml \
    --extrinsic config/extrinsic.yaml

### 5. 查看使用示例
python examples/calibration_example.py
python examples/realtime_usage.py

## 常用命令

# 查看帮助
python scripts/capture_calibration_images.py --help
python scripts/calibrate_intrinsic.py --help
python scripts/calibrate_extrinsic_manual.py --help
python scripts/verify_calibration.py --help
