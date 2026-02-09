#!/usr/bin/env python3
"""
快速测试实时3D显示功能
"""
import sys
import os
import matplotlib

print("\n" + "="*70)
print("实时3D显示功能测试")
print("="*70 + "\n")

# 检查matplotlib后端
backend = matplotlib.get_backend()
print(f"1. Matplotlib Backend: {backend}")

if backend.lower() == 'agg':
    print("   ⚠ 警告: 使用非GUI后端（Agg）")
    print("   → 尝试切换到TkAgg...")
    try:
        matplotlib.use('TkAgg', force=True)
        backend = matplotlib.get_backend()
        print(f"   ✓ 成功切换到: {backend}")
    except:
        try:
            matplotlib.use('Qt5Agg', force=True)
            backend = matplotlib.get_backend()
            print(f"   ✓ 成功切换到: {backend}")
        except:
            print("   ✗ 无法切换到GUI后端")
            print("   → 请安装: sudo apt-get install python3-tk")
            print("   → 或者: pip install PyQt5")
            sys.exit(1)
else:
    print(f"   ✓ 已使用GUI后端: {backend}")

# 测试基础依赖
print("\n2. 检查依赖包:")
packages = {
    'numpy': None,
    'matplotlib': None,
    'mpl_toolkits.mplot3d': None,
}

for pkg in packages:
    try:
        if pkg == 'mpl_toolkits.mplot3d':
            from mpl_toolkits.mplot3d import Axes3D
            print(f"   ✓ {pkg}")
        else:
            __import__(pkg)
            print(f"   ✓ {pkg}")
    except ImportError as e:
        print(f"   ✗ {pkg}: {e}")
        sys.exit(1)

# 测试项目模块
print("\n3. 检查项目模块:")
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from src.calibration import ExtrinsicCalibration
    print("   ✓ src.calibration")
except ImportError as e:
    print(f"   ✗ src.calibration: {e}")
    sys.exit(1)

# 测试创建外参
print("\n4. 测试外参创建:")
try:
    calibrator = ExtrinsicCalibration()
    extrinsic_data = calibrator.from_manual_measurement(
        position=(1.5, 0.0, 1.8),
        orientation=(0.0, -10.0, 0.0),
        angle_unit='degree'
    )
    print(f"   ✓ 位置: {extrinsic_data['translation_vector']}")
    print(f"   ✓ 姿态: roll={extrinsic_data['euler_angles']['roll']:.1f}°, "
          f"pitch={extrinsic_data['euler_angles']['pitch']:.1f}°, "
          f"yaw={extrinsic_data['euler_angles']['yaw']:.1f}°")
except Exception as e:
    print(f"   ✗ 失败: {e}")
    sys.exit(1)

# 测试导入交互式可视化函数
print("\n5. 测试交互式可视化模块:")
try:
    # 添加scripts目录到路径
    scripts_dir = os.path.join(os.path.dirname(__file__), 'scripts')
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    
    from view_3d_interactive import plot_camera_pose_3d_interactive
    print("   ✓ plot_camera_pose_3d_interactive 导入成功")
except ImportError as e:
    print(f"   ✗ 导入失败: {e}")
    sys.exit(1)

# 显示测试结果
print("\n" + "="*70)
print("所有测试通过！")
print("="*70)

print("\n现在可以使用以下方式启动实时3D显示:\n")

print("方式1: 使用外参文件")
print("  python scripts/view_3d_interactive.py --extrinsic config/extrinsic.yaml\n")

print("方式2: 命令行指定位置")
print("  python scripts/view_3d_interactive.py \\")
print("      --position 1.5 0.0 1.8 \\")
print("      --orientation 0.0 -10.0 0.0\n")

print("方式3: 多相机位置测试")
print("  python examples/test_interactive_3d.py\n")

print("方式4: 在Python代码中使用")
print("  import sys, os")
print("  sys.path.insert(0, 'scripts')")
print("  from view_3d_interactive import plot_camera_pose_3d_interactive")
print("  plot_camera_pose_3d_interactive(extrinsic_data)\n")

# 询问是否立即测试
import time
print("="*70)
response = input("\n是否立即显示交互式3D可视化? (y/n): ").strip().lower()

if response == 'y':
    print("\n启动交互式3D显示...")
    print("操作提示:")
    print("  • 鼠标左键: 旋转")
    print("  • 鼠标右键: 平移")
    print("  • 滚轮: 缩放")
    print("  • 按 'r': 重置")
    print("  • 按 's': 保存")
    print("  • 按 'q': 退出\n")
    
    time.sleep(1)
    
    success = plot_camera_pose_3d_interactive(
        extrinsic_data=extrinsic_data,
        show_camera_frame=True,
        car_length=4.0,
        car_width=2.0,
        enable_animation=False
    )
    
    if success:
        print("\n✓ 交互式3D显示已关闭")
    else:
        print("\n✗ 显示失败")
else:
    print("\n跳过交互式测试")
    print("稍后可手动运行上述命令进行测试\n")

print("="*70)
print("测试完成！")
print("="*70 + "\n")
