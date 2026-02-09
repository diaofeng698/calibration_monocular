#!/usr/bin/env python3
"""
手动测量外参标定
通过物理测量设置相机外参
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import argparse
import numpy as np
from src.calibration import ExtrinsicCalibration
from src.utils import save_calibration, visualize_calibration, plot_camera_pose_3d


def main():
    parser = argparse.ArgumentParser(description='手动测量外参标定')
    parser.add_argument('--output', type=str, default='config/extrinsic.yaml',
                       help='输出文件路径')
    parser.add_argument('--position', type=float, nargs=3,
                       help='相机位置 (x y z) 单位:米，相对于后轴中心')
    parser.add_argument('--orientation', type=float, nargs=3,
                       help='相机姿态 (roll pitch yaw) 单位:度')
    parser.add_argument('--interactive', action='store_true',
                       help='交互式输入参数')
    args = parser.parse_args()
    
    print("\n" + "="*60)
    print("相机外参标定 - 手动测量方法")
    print("="*60)
    print("\n坐标系定义:")
    print("  车辆坐标系: 原点在后轴中心")
    print("    X轴: 向前为正")
    print("    Y轴: 向左为正")
    print("    Z轴: 向上为正")
    print("\n  姿态角定义:")
    print("    Roll:  绕X轴旋转 (左右倾斜)")
    print("    Pitch: 绕Y轴旋转 (俯仰)")
    print("    Yaw:   绕Z轴旋转 (偏航)")
    print("="*60 + "\n")
    
    # 获取相机位置和姿态
    if args.interactive or args.position is None or args.orientation is None:
        print("请输入相机相对于后轴中心的位置和姿态:\n")
        
        print("位置 (单位: 米):")
        x = float(input("  X (向前距离): "))
        y = float(input("  Y (向左距离): "))
        z = float(input("  Z (向上高度): "))
        position = (x, y, z)
        
        print("\n姿态 (单位: 度):")
        roll = float(input("  Roll  (左右倾斜): "))
        pitch = float(input("  Pitch (俯仰角度): "))
        yaw = float(input("  Yaw   (偏航角度): "))
        orientation = (roll, pitch, yaw)
    else:
        position = tuple(args.position)
        orientation = tuple(args.orientation)
    
    print("\n" + "-"*60)
    print("标定参数:")
    print(f"  位置: X={position[0]:.3f}m, Y={position[1]:.3f}m, Z={position[2]:.3f}m")
    print(f"  姿态: Roll={orientation[0]:.2f}°, Pitch={orientation[1]:.2f}°, Yaw={orientation[2]:.2f}°")
    print("-"*60 + "\n")
    
    # 执行标定
    calibrator = ExtrinsicCalibration()
    result = calibrator.from_manual_measurement(
        position=position,
        orientation=orientation,
        angle_unit='degree'
    )
    
    # 保存结果
    save_calibration(result, args.output)
    
    # 可视化结果
    print("\n")
    visualize_calibration({}, result)
    
    # 3D可视化
    print("\n生成3D可视化...")
    output_dir = os.path.dirname(args.output)
    viz_path = os.path.join(output_dir, 'camera_pose_3d.png')
    try:
        plot_camera_pose_3d(result, save_path=viz_path)
    except Exception as e:
        print(f"警告: 无法生成3D可视化 (可能是无GUI环境): {e}")
        print("跳过3D可视化...")
    
    print("\n✓ 外参标定完成!")
    print(f"结果已保存到: {args.output}")
    
    # 示例：测试坐标变换
    print("\n" + "="*60)
    print("坐标变换示例")
    print("="*60)
    print("\n假设相机坐标系中有一个点: (0, 0, 2.0) 米 (相机前方2米)")
    
    point_camera = np.array([0, 0, 2.0])
    point_vehicle = calibrator.transform_point_to_vehicle(point_camera)
    
    print(f"转换到车辆坐标系: ({point_vehicle[0]:.3f}, {point_vehicle[1]:.3f}, {point_vehicle[2]:.3f}) 米")
    print("="*60 + "\n")


if __name__ == '__main__':
    main()
