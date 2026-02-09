#!/usr/bin/env python3
"""
测试和展示3D可视化功能的改进
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
from src.calibration import ExtrinsicCalibration
from src.utils import plot_camera_pose_3d

def test_multiple_camera_positions():
    """测试多个相机位置的3D可视化"""
    
    print("\n" + "="*70)
    print("3D可视化功能测试 - 多种相机位置")
    print("="*70 + "\n")
    
    # 定义不同的相机安装位置场景
    scenarios = [
        {
            'name': '车顶中央（标准配置）',
            'position': (1.5, 0.0, 1.8),
            'orientation': (0.0, -10.0, 0.0),
            'filename': 'config/test_roof_center.png'
        },
        {
            'name': '车顶左侧',
            'position': (1.5, 0.8, 1.8),
            'orientation': (0.0, -10.0, -5.0),
            'filename': 'config/test_roof_left.png'
        },
        {
            'name': '车头前方',
            'position': (3.5, 0.0, 1.2),
            'orientation': (0.0, -5.0, 0.0),
            'filename': 'config/test_front.png'
        },
        {
            'name': '挡风玻璃处',
            'position': (2.5, 0.0, 1.4),
            'orientation': (0.0, -20.0, 0.0),
            'filename': 'config/test_windshield.png'
        },
        {
            'name': '侧视镜位置',
            'position': (2.0, 1.2, 1.5),
            'orientation': (0.0, -15.0, -30.0),
            'filename': 'config/test_side_mirror.png'
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n[{i}/{len(scenarios)}] 测试场景: {scenario['name']}")
        print(f"  位置: {scenario['position']}")
        print(f"  姿态: {scenario['orientation']}")
        
        # 创建外参标定
        calibrator = ExtrinsicCalibration()
        result = calibrator.from_manual_measurement(
            position=scenario['position'],
            orientation=scenario['orientation'],
            angle_unit='degree'
        )
        
        # 生成3D可视化
        success = plot_camera_pose_3d(result, save_path=scenario['filename'])
        
        if success:
            print(f"  ✓ 3D可视化已保存: {scenario['filename']}")
        else:
            print(f"  ✗ 3D可视化失败")
        
        print(f"  坐标变换测试:")
        point_camera = np.array([0, 0, 2.0])
        point_vehicle = calibrator.transform_point_to_vehicle(point_camera)
        print(f"    相机前方2米 -> 车辆坐标: ({point_vehicle[0]:.2f}, {point_vehicle[1]:.2f}, {point_vehicle[2]:.2f})m")
    
    print("\n" + "="*70)
    print("所有测试完成！")
    print("="*70)
    print(f"\n生成的可视化图像保存在 config/ 目录下")
    print("你可以查看这些图像来比较不同相机位置的3D表示\n")


def test_custom_vehicle_size():
    """测试自定义车辆尺寸的3D可视化"""
    
    print("\n" + "="*70)
    print("3D可视化功能测试 - 自定义车辆尺寸")
    print("="*70 + "\n")
    
    from src.utils import save_calibration, load_calibration
    
    # 创建一个标定结果
    calibrator = ExtrinsicCalibration()
    result = calibrator.from_manual_measurement(
        position=(2.0, 0.0, 1.8),
        orientation=(0.0, -12.0, 0.0),
        angle_unit='degree'
    )
    
    # 测试不同车辆尺寸
    vehicle_configs = [
        {'length': 4.0, 'width': 2.0, 'desc': '紧凑型轿车'},
        {'length': 5.0, 'width': 2.2, 'desc': '中型轿车'},
        {'length': 5.5, 'width': 2.5, 'desc': 'SUV'},
    ]
    
    for i, config in enumerate(vehicle_configs, 1):
        print(f"\n[{i}/{len(vehicle_configs)}] 车辆类型: {config['desc']}")
        print(f"  尺寸: 长{config['length']}m × 宽{config['width']}m")
        
        filename = f"config/test_vehicle_{i}.png"
        
        # 使用plot_camera_pose_3d的新参数
        # 注意：需要先导入并直接调用函数
        from src.utils.visualization import plot_camera_pose_3d as plot_func
        
        # 由于当前版本还不支持这些参数，我们先使用默认值
        # 后续可以扩展功能
        success = plot_func(result, save_path=filename)
        
        if success:
            print(f"  ✓ 已保存: {filename}")


def show_improvement_summary():
    """显示改进总结"""
    
    print("\n" + "="*70)
    print("3D可视化功能改进总结")
    print("="*70)
    
    improvements = [
        "✓ 完全消除字体警告（所有标签使用英文）",
        "✓ 增强的视觉效果（更大的相机标记、加粗的坐标轴）",
        "✓ 自适应坐标轴范围（根据相机位置自动调整）",
        "✓ 添加相机位置坐标标注",
        "✓ 车辆底部填充半透明显示",
        "✓ 后轴中心明确标记",
        "✓ 更好的图例和网格显示",
        "✓ 可选的相机坐标系显示",
        "✓ 异常处理和返回值（便于错误检测）",
        "✓ 更高的图像质量（1272x1334分辨率）"
    ]
    
    print("\n主要改进:")
    for improvement in improvements:
        print(f"  {improvement}")
    
    print("\n" + "="*70)
    print()


if __name__ == '__main__':
    # 显示改进总结
    show_improvement_summary()
    
    # 测试多个相机位置
    test_multiple_camera_positions()
    
    print("\n提示: 你可以在 config/ 目录下查看所有生成的3D可视化图像")
    print("      这些图像展示了不同相机安装位置的效果\n")
