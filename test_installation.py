#!/usr/bin/env python3
"""
测试工程安装和基本功能
"""
import sys
import os

def test_imports():
    """测试模块导入"""
    print("="*60)
    print("测试模块导入...")
    print("="*60)
    
    try:
        import numpy
        print("✓ numpy")
    except ImportError as e:
        print(f"✗ numpy: {e}")
        return False
    
    try:
        import cv2
        print(f"✓ opencv-python (version: {cv2.__version__})")
    except ImportError as e:
        print(f"✗ opencv-python: {e}")
        return False
    
    try:
        import yaml
        print("✓ pyyaml")
    except ImportError as e:
        print(f"✗ pyyaml: {e}")
        return False
    
    try:
        import matplotlib
        print("✓ matplotlib")
    except ImportError as e:
        print(f"✗ matplotlib: {e}")
        return False
    
    try:
        import scipy
        print("✓ scipy")
    except ImportError as e:
        print(f"✗ scipy: {e}")
        return False
    
    try:
        import transforms3d
        print("✓ transforms3d")
    except ImportError as e:
        print(f"✗ transforms3d: {e}")
        return False
    
    try:
        import pyrealsense2
        print("✓ pyrealsense2 (相机SDK)")
    except ImportError:
        print("⚠ pyrealsense2 未安装（相机将在模拟模式下运行）")
    
    return True


def test_project_modules():
    """测试项目模块"""
    print("\n" + "="*60)
    print("测试项目模块...")
    print("="*60)
    
    try:
        from src.camera import FemtoBoltCamera
        print("✓ src.camera.FemtoBoltCamera")
    except ImportError as e:
        print(f"✗ src.camera: {e}")
        return False
    
    try:
        from src.calibration import IntrinsicCalibration, ExtrinsicCalibration
        print("✓ src.calibration.IntrinsicCalibration")
        print("✓ src.calibration.ExtrinsicCalibration")
    except ImportError as e:
        print(f"✗ src.calibration: {e}")
        return False
    
    try:
        from src.utils import save_calibration, load_calibration
        print("✓ src.utils.save_calibration")
        print("✓ src.utils.load_calibration")
    except ImportError as e:
        print(f"✗ src.utils: {e}")
        return False
    
    return True


def test_basic_functionality():
    """测试基本功能"""
    print("\n" + "="*60)
    print("测试基本功能...")
    print("="*60)
    
    import numpy as np
    from src.calibration import ExtrinsicCalibration
    
    try:
        # 测试外参标定
        calib = ExtrinsicCalibration()
        result = calib.from_manual_measurement(
            position=(1.5, 0.0, 1.8),
            orientation=(0.0, -10.0, 0.0),
            angle_unit='degree'
        )
        print("✓ 外参标定基本功能")
        
        # 测试坐标转换
        point_camera = np.array([0, 0, 2.0])
        point_vehicle = calib.transform_point_to_vehicle(point_camera)
        print(f"✓ 坐标转换: 相机{point_camera} -> 车辆{point_vehicle}")
        
    except Exception as e:
        print(f"✗ 基本功能测试失败: {e}")
        return False
    
    return True


def test_file_structure():
    """测试文件结构"""
    print("\n" + "="*60)
    print("测试文件结构...")
    print("="*60)
    
    required_dirs = [
        'src',
        'src/camera',
        'src/calibration',
        'src/utils',
        'scripts',
        'examples',
        'config',
        'data',
        'data/intrinsic_calibration',
        'data/extrinsic_calibration'
    ]
    
    required_files = [
        'README.md',
        'USAGE.md',
        'requirements.txt',
        'scripts/capture_calibration_images.py',
        'scripts/calibrate_intrinsic.py',
        'scripts/calibrate_extrinsic_manual.py',
        'scripts/verify_calibration.py'
    ]
    
    all_ok = True
    
    for dir_path in required_dirs:
        if os.path.isdir(dir_path):
            print(f"✓ {dir_path}/")
        else:
            print(f"✗ {dir_path}/ (不存在)")
            all_ok = False
    
    for file_path in required_files:
        if os.path.isfile(file_path):
            print(f"✓ {file_path}")
        else:
            print(f"✗ {file_path} (不存在)")
            all_ok = False
    
    return all_ok


def main():
    """主函数"""
    print("\n" + "="*60)
    print("Femto Bolt 相机标定工程 - 安装测试")
    print("="*60 + "\n")
    
    # 检查Python版本
    import sys
    print(f"Python版本: {sys.version}")
    if sys.version_info < (3, 7):
        print("⚠ 警告: 推荐使用Python 3.7或更高版本\n")
    else:
        print("✓ Python版本满足要求\n")
    
    # 运行测试
    tests = [
        ("文件结构", test_file_structure),
        ("依赖库导入", test_imports),
        ("项目模块", test_project_modules),
        ("基本功能", test_basic_functionality)
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n✗ {test_name}测试异常: {e}")
            results[test_name] = False
    
    # 总结
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)
    
    for test_name, result in results.items():
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{test_name}: {status}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n" + "="*60)
        print("🎉 所有测试通过！工程已正确安装。")
        print("="*60)
        print("\n下一步:")
        print("1. 查看 README.md 了解项目概述")
        print("2. 查看 USAGE.md 了解详细使用说明")
        print("3. 运行 python examples/calibration_example.py 查看示例")
        print("4. 开始标定: python scripts/capture_calibration_images.py")
        print("="*60 + "\n")
        return 0
    else:
        print("\n" + "="*60)
        print("⚠ 部分测试失败")
        print("="*60)
        print("\n请检查:")
        print("1. 是否正确安装了所有依赖: pip install -r requirements.txt")
        print("2. 是否在正确的目录下运行测试")
        print("="*60 + "\n")
        return 1


if __name__ == '__main__':
    exit(main())
