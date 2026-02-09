#!/usr/bin/env python3
"""
实时3D可视化完整示例
演示如何在实际应用中使用交互式3D显示
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from src.calibration import ExtrinsicCalibration
from view_3d_interactive import plot_camera_pose_3d_interactive
import matplotlib
matplotlib.use('TkAgg')  # 确保使用GUI后端


def example1_basic_usage():
    """示例1: 基础用法 - 单个相机位置"""
    print("\n" + "="*70)
    print("示例1: 基础用法 - 单个相机位置")
    print("="*70 + "\n")
    
    # 创建外参标定器
    calibrator = ExtrinsicCalibration()
    
    # 设置相机位置（前置中央相机）
    position = (1.5, 0.0, 1.8)  # 前方1.5m，高度1.8m
    orientation = (0.0, -10.0, 0.0)  # 俯仰角-10度
    
    print(f"相机位置: {position}")
    print(f"相机姿态: {orientation}")
    
    # 计算外参
    extrinsic = calibrator.from_manual_measurement(
        position=position,
        orientation=orientation,
        angle_unit='degree'
    )
    
    # 显示交互式3D可视化
    print("\n启动交互式3D显示...")
    plot_camera_pose_3d_interactive(
        extrinsic_data=extrinsic,
        show_camera_frame=True,
        car_length=4.0,
        car_width=2.0
    )


def example2_multiple_views():
    """示例2: 依次显示多个视角"""
    print("\n" + "="*70)
    print("示例2: 依次显示多个相机位置")
    print("="*70 + "\n")
    
    calibrator = ExtrinsicCalibration()
    
    # 定义多个相机配置
    camera_configs = [
        {
            'name': '前置中央相机',
            'position': (2.0, 0.0, 1.5),
            'orientation': (0, -15, 0),
        },
        {
            'name': '前置左侧相机',
            'position': (1.8, 0.8, 1.5),
            'orientation': (0, -15, 10),
        },
        {
            'name': '前置右侧相机',
            'position': (1.8, -0.8, 1.5),
            'orientation': (0, -15, -10),
        },
        {
            'name': '后置相机',
            'position': (-0.5, 0.0, 2.0),
            'orientation': (0, -20, 180),
        }
    ]
    
    # 依次显示每个相机
    for i, config in enumerate(camera_configs, 1):
        print(f"\n[{i}/{len(camera_configs)}] {config['name']}")
        print(f"  位置: {config['position']}")
        print(f"  姿态: {config['orientation']}")
        
        extrinsic = calibrator.from_manual_measurement(
            position=config['position'],
            orientation=config['orientation'],
            angle_unit='degree'
        )
        
        print("  显示3D可视化（关闭窗口后自动显示下一个）...")
        plot_camera_pose_3d_interactive(
            extrinsic_data=extrinsic,
            show_camera_frame=True,
            car_length=4.0,
            car_width=2.0
        )


def example3_with_animation():
    """示例3: 自动旋转动画"""
    print("\n" + "="*70)
    print("示例3: 自动旋转动画")
    print("="*70 + "\n")
    
    calibrator = ExtrinsicCalibration()
    
    # 前置相机
    extrinsic = calibrator.from_manual_measurement(
        position=(1.5, 0.0, 1.8),
        orientation=(0.0, -10.0, 0.0),
        angle_unit='degree'
    )
    
    print("启动自动旋转动画...")
    print("提示: 动画会360度旋转展示相机位置")
    print("      仍可使用鼠标手动控制")
    
    plot_camera_pose_3d_interactive(
        extrinsic_data=extrinsic,
        show_camera_frame=True,
        car_length=4.0,
        car_width=2.0,
        enable_animation=True  # 启用动画
    )


def example4_custom_vehicle():
    """示例4: 自定义车辆尺寸"""
    print("\n" + "="*70)
    print("示例4: 自定义车辆尺寸")
    print("="*70 + "\n")
    
    calibrator = ExtrinsicCalibration()
    
    # SUV相机配置
    car_length = 5.0  # 5米长的SUV
    car_width = 2.2   # 2.2米宽
    
    extrinsic = calibrator.from_manual_measurement(
        position=(2.5, 0.0, 1.9),  # 相机位置适配更大的车辆
        orientation=(0.0, -12.0, 0.0),
        angle_unit='degree'
    )
    
    print(f"车辆尺寸: 长{car_length}m × 宽{car_width}m")
    print(f"相机位置: (2.5, 0.0, 1.9)")
    
    plot_camera_pose_3d_interactive(
        extrinsic_data=extrinsic,
        show_camera_frame=True,
        car_length=car_length,
        car_width=car_width
    )


def example5_load_from_file():
    """示例5: 从文件加载外参"""
    print("\n" + "="*70)
    print("示例5: 从文件加载外参")
    print("="*70 + "\n")
    
    from src.utils import load_calibration, save_calibration
    
    # 首先创建并保存一个外参文件
    calibrator = ExtrinsicCalibration()
    extrinsic = calibrator.from_manual_measurement(
        position=(1.5, 0.0, 1.8),
        orientation=(0.0, -10.0, 0.0),
        angle_unit='degree'
    )
    
    # 保存到临时文件
    temp_file = '/tmp/test_extrinsic.yaml'
    save_calibration(extrinsic, temp_file)
    print(f"已保存外参到: {temp_file}")
    
    # 从文件加载
    loaded_extrinsic = load_calibration(temp_file)
    print(f"已从文件加载外参")
    
    # 显示
    print("\n显示加载的外参...")
    plot_camera_pose_3d_interactive(
        extrinsic_data=loaded_extrinsic,
        show_camera_frame=True,
        car_length=4.0,
        car_width=2.0
    )


def example6_practical_workflow():
    """示例6: 实际标定工作流"""
    print("\n" + "="*70)
    print("示例6: 实际标定工作流")
    print("="*70 + "\n")
    
    from src.utils import save_calibration
    
    # 步骤1: 测量相机物理位置
    print("步骤1: 测量相机物理位置")
    print("  - 使用卷尺测量相机到后轴中心的距离")
    print("  - 测量X（前后）、Y（左右）、Z（高度）")
    
    measured_position = (1.5, 0.0, 1.8)
    print(f"  测量结果: {measured_position}\n")
    
    # 步骤2: 测量或估计相机姿态
    print("步骤2: 测量相机姿态")
    print("  - 使用水平仪或目测估计俯仰角")
    print("  - 测量横滚角和偏航角")
    
    measured_orientation = (0.0, -10.0, 0.0)
    print(f"  测量结果: roll={measured_orientation[0]}°, "
          f"pitch={measured_orientation[1]}°, yaw={measured_orientation[2]}°\n")
    
    # 步骤3: 创建外参
    print("步骤3: 计算外参矩阵")
    calibrator = ExtrinsicCalibration()
    extrinsic = calibrator.from_manual_measurement(
        position=measured_position,
        orientation=measured_orientation,
        angle_unit='degree'
    )
    print("  ✓ 外参矩阵计算完成\n")
    
    # 步骤4: 可视化验证
    print("步骤4: 可视化验证")
    print("  - 查看相机位置是否合理")
    print("  - 检查相机朝向是否正确")
    print("  - 使用交互式3D图旋转查看")
    
    response = input("\n  是否显示3D可视化? (y/n): ").strip().lower()
    if response == 'y':
        print("\n  启动3D可视化...")
        plot_camera_pose_3d_interactive(
            extrinsic_data=extrinsic,
            show_camera_frame=True,
            car_length=4.0,
            car_width=2.0
        )
    
    # 步骤5: 保存结果
    print("\n步骤5: 保存标定结果")
    output_path = 'config/extrinsic.yaml'
    
    response = input(f"  是否保存外参到 {output_path}? (y/n): ").strip().lower()
    if response == 'y':
        os.makedirs('config', exist_ok=True)
        save_calibration(extrinsic, output_path)
        print(f"  ✓ 已保存到: {output_path}")
    
    print("\n" + "="*70)
    print("标定工作流完成！")
    print("="*70)


def main():
    """主函数 - 显示所有示例"""
    print("\n" + "="*70)
    print("实时3D可视化完整示例")
    print("="*70)
    
    examples = [
        ("基础用法 - 单个相机位置", example1_basic_usage),
        ("依次显示多个相机位置", example2_multiple_views),
        ("自动旋转动画", example3_with_animation),
        ("自定义车辆尺寸", example4_custom_vehicle),
        ("从文件加载外参", example5_load_from_file),
        ("实际标定工作流", example6_practical_workflow),
    ]
    
    print("\n可用示例:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")
    
    print("\n  0. 运行所有示例")
    print("  q. 退出")
    
    while True:
        choice = input("\n请选择示例编号 (0-6, q): ").strip()
        
        if choice == 'q':
            print("退出")
            break
        
        try:
            choice_num = int(choice)
            
            if choice_num == 0:
                # 运行所有示例
                for name, func in examples:
                    print(f"\n{'='*70}")
                    print(f"运行: {name}")
                    print('='*70)
                    func()
                break
            elif 1 <= choice_num <= len(examples):
                # 运行选定的示例
                examples[choice_num - 1][1]()
                break
            else:
                print("无效的选择，请输入0-6之间的数字")
        except ValueError:
            print("无效的输入，请输入数字或'q'")


if __name__ == '__main__':
    # 检查matplotlib后端
    backend = matplotlib.get_backend()
    print(f"\nMatplotlib Backend: {backend}")
    
    if backend.lower() == 'agg':
        print("\n⚠ 警告: 当前使用非GUI后端（Agg）")
        print("交互式3D显示将无法使用")
        print("\n请尝试:")
        print("  1. 安装tkinter: sudo apt-get install python3-tk")
        print("  2. 或安装PyQt5: pip install PyQt5")
        print("  3. 或设置环境变量: export MPLBACKEND=TkAgg")
        sys.exit(1)
    
    main()
