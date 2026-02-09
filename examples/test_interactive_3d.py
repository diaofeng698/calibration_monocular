#!/usr/bin/env python3
"""
测试交互式3D可视化功能
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.calibration import ExtrinsicCalibration
import matplotlib
# 使用交互式后端
try:
    matplotlib.use('TkAgg')
except:
    try:
        matplotlib.use('Qt5Agg')
    except:
        print("Warning: No GUI backend available")

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np


def plot_multiple_camera_positions():
    """
    在同一个图中显示多个相机位置
    可以交互式查看
    """
    
    # 定义多个相机位置
    camera_positions = [
        {
            'name': 'Front Center',
            'position': (2.0, 0.0, 1.5),
            'orientation': (0, -15, 0),
            'color': 'red'
        },
        {
            'name': 'Front Left',
            'position': (1.8, 0.8, 1.5),
            'orientation': (0, -15, 10),
            'color': 'blue'
        },
        {
            'name': 'Front Right',
            'position': (1.8, -0.8, 1.5),
            'orientation': (0, -15, -10),
            'color': 'green'
        },
        {
            'name': 'Rear View',
            'position': (-0.5, 0.0, 2.0),
            'orientation': (0, -20, 180),
            'color': 'orange'
        }
    ]
    
    # 创建3D图形
    fig = plt.figure(figsize=(16, 12))
    ax = fig.add_subplot(111, projection='3d')
    
    # 绘制车辆坐标系
    axis_length = 2.0
    ax.quiver(0, 0, 0, axis_length, 0, 0, 
             color='red', arrow_length_ratio=0.15, linewidth=2.5, 
             label='X (Forward)', alpha=0.8)
    ax.quiver(0, 0, 0, 0, axis_length, 0, 
             color='green', arrow_length_ratio=0.15, linewidth=2.5, 
             label='Y (Left)', alpha=0.8)
    ax.quiver(0, 0, 0, 0, 0, axis_length, 
             color='blue', arrow_length_ratio=0.15, linewidth=2.5, 
             label='Z (Up)', alpha=0.8)
    
    # 绘制车辆轮廓
    car_length, car_width = 4.0, 2.0
    car_corners = np.array([
        [0, -car_width/2, 0],
        [car_length, -car_width/2, 0],
        [car_length, car_width/2, 0],
        [0, car_width/2, 0],
        [0, -car_width/2, 0]
    ])
    ax.plot(car_corners[:, 0], car_corners[:, 1], car_corners[:, 2], 
           'k-', linewidth=3, label='Vehicle', alpha=0.8)
    
    # 填充车辆底部
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    verts = [car_corners[:-1]]
    poly = Poly3DCollection(verts, alpha=0.2, facecolor='gray', edgecolor='black')
    ax.add_collection3d(poly)
    
    # 后轴标记
    ax.scatter(0, 0, 0, c='black', s=100, marker='o', label='Rear Axle Center')
    
    # 绘制所有相机位置
    calibrator = ExtrinsicCalibration()
    
    for cam in camera_positions:
        # 计算外参
        extrinsic = calibrator.from_manual_measurement(
            position=cam['position'],
            orientation=cam['orientation'],
            angle_unit='degree'
        )
        
        translation = np.array(extrinsic['translation_vector'])
        rotation_matrix = np.array(extrinsic['rotation_matrix'])
        
        # 绘制相机位置
        ax.scatter(translation[0], translation[1], translation[2], 
                  c=cam['color'], s=300, marker='^', 
                  edgecolors='black', linewidth=2,
                  label=cam['name'], zorder=10, alpha=0.8)
        
        # 添加标注
        ax.text(translation[0], translation[1], translation[2] + 0.3,
               cam['name'],
               fontsize=9, ha='center', fontweight='bold')
        
        # 绘制相机朝向（光轴）
        camera_axis_length = 1.0
        camera_z_axis = rotation_matrix[:, 2] * camera_axis_length
        ax.quiver(translation[0], translation[1], translation[2],
                 camera_z_axis[0], camera_z_axis[1], camera_z_axis[2],
                 color=cam['color'], arrow_length_ratio=0.2, linewidth=2,
                 linestyle='--', alpha=0.6)
    
    # 设置标签和标题
    ax.set_xlabel('X (Forward) [m]', fontsize=11, fontweight='bold')
    ax.set_ylabel('Y (Left) [m]', fontsize=11, fontweight='bold')
    ax.set_zlabel('Z (Up) [m]', fontsize=11, fontweight='bold')
    ax.set_title('Multiple Camera Positions (Interactive View)', 
                fontsize=14, fontweight='bold', pad=20)
    
    # 设置图例
    ax.legend(loc='upper left', fontsize=9, framealpha=0.9, ncol=2)
    
    # 设置坐标轴范围
    ax.set_xlim([-1, 5])
    ax.set_ylim([-2, 2])
    ax.set_zlim([-0.5, 3])
    
    ax.set_box_aspect([1.2, 0.8, 0.7])
    ax.grid(True, alpha=0.3)
    ax.view_init(elev=25, azim=45)
    
    # 添加说明文字
    info_text = (
        "Interactive 3D Visualization - Multiple Cameras\n"
        "• Left Mouse: Rotate view\n"
        "• Right Mouse: Pan view\n"
        "• Scroll: Zoom in/out\n"
        "• Press 'q': Close window"
    )
    fig.text(0.02, 0.98, info_text, transform=fig.transFigure,
            fontsize=9, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    plt.tight_layout()
    
    print("\n" + "="*70)
    print("Interactive 3D Visualization - Multiple Camera Positions")
    print("="*70)
    print("\nCamera Positions:")
    for i, cam in enumerate(camera_positions, 1):
        print(f"  {i}. {cam['name']}: {cam['position']}")
    print("\nControls:")
    print("  • Mouse Left: Rotate")
    print("  • Mouse Right: Pan")
    print("  • Scroll: Zoom")
    print("  • Press 'q': Quit")
    print("\n" + "="*70 + "\n")
    
    try:
        plt.show()
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False


def main():
    """主函数"""
    print("\n" + "="*70)
    print("测试交互式3D可视化功能")
    print("="*70 + "\n")
    
    backend = matplotlib.get_backend()
    print(f"Matplotlib Backend: {backend}")
    
    if backend.lower() == 'agg':
        print("\n⚠ Warning: Using non-GUI backend (Agg)")
        print("  Interactive features will not be available")
        print("  Try setting MPLBACKEND environment variable:")
        print("    export MPLBACKEND=TkAgg")
        print("    or")
        print("    export MPLBACKEND=Qt5Agg")
        return
    
    print(f"✓ Using GUI backend: {backend}")
    print("  Interactive features enabled!\n")
    
    # 测试多相机位置可视化
    success = plot_multiple_camera_positions()
    
    if success:
        print("\n✓ Interactive visualization completed")
    else:
        print("\n✗ Failed to display interactive visualization")


if __name__ == '__main__':
    main()
