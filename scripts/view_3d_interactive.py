#!/usr/bin/env python3
"""
实时3D可视化工具
支持交互式3D显示，可以旋转、缩放查看相机位置
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib
# 使用交互式后端
try:
    matplotlib.use('TkAgg')  # 尝试使用TkAgg
except:
    try:
        matplotlib.use('Qt5Agg')  # 或Qt5Agg
    except:
        matplotlib.use('Agg')  # 降级到非GUI后端
        print("Warning: No GUI backend available, switching to Agg")

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.widgets import Slider, Button
import argparse


def plot_camera_pose_3d_interactive(extrinsic_data: dict, 
                                    show_camera_frame: bool = True,
                                    car_length: float = 4.0, 
                                    car_width: float = 2.0,
                                    enable_animation: bool = False):
    """
    交互式3D可视化相机在车辆坐标系中的位置
    
    Args:
        extrinsic_data: 外参标定结果
        show_camera_frame: 是否显示相机坐标系
        car_length: 车辆长度（米）
        car_width: 车辆宽度（米）
        enable_animation: 是否启用自动旋转动画
    """
    
    # 获取相机位置
    translation = np.array(extrinsic_data['translation_vector'])
    rotation_matrix = np.array(extrinsic_data['rotation_matrix'])
    
    # 创建图形
    fig = plt.figure(figsize=(14, 10))
    ax = fig.add_subplot(111, projection='3d')
    
    # 计算坐标轴长度
    max_dist = max(abs(translation[0]), abs(translation[1]), abs(translation[2]), car_length)
    axis_length = max(2.0, max_dist * 0.3)
    
    def draw_scene(elev=25, azim=45):
        """绘制场景"""
        ax.clear()
        
        # 绘制车辆坐标系
        ax.quiver(0, 0, 0, axis_length, 0, 0, 
                 color='red', arrow_length_ratio=0.15, linewidth=2.5, 
                 label='X (Forward)', alpha=0.8)
        ax.quiver(0, 0, 0, 0, axis_length, 0, 
                 color='green', arrow_length_ratio=0.15, linewidth=2.5, 
                 label='Y (Left)', alpha=0.8)
        ax.quiver(0, 0, 0, 0, 0, axis_length, 
                 color='blue', arrow_length_ratio=0.15, linewidth=2.5, 
                 label='Z (Up)', alpha=0.8)
        
        # 绘制相机位置
        ax.scatter(translation[0], translation[1], translation[2], 
                  c='orange', s=300, marker='^', 
                  edgecolors='black', linewidth=2,
                  label='Camera', zorder=10)
        
        # 添加相机位置标注
        ax.text(translation[0], translation[1], translation[2] + 0.3,
               f'({translation[0]:.1f}, {translation[1]:.1f}, {translation[2]:.1f})',
               fontsize=9, ha='center')
        
        # 绘制相机坐标系
        if show_camera_frame:
            camera_axis_length = axis_length * 0.4
            camera_axes = rotation_matrix * camera_axis_length
            
            ax.quiver(translation[0], translation[1], translation[2],
                     camera_axes[0, 0], camera_axes[1, 0], camera_axes[2, 0],
                     color='lightcoral', arrow_length_ratio=0.2, linewidth=2,
                     linestyle='--', alpha=0.7, label='Cam X')
            ax.quiver(translation[0], translation[1], translation[2],
                     camera_axes[0, 1], camera_axes[1, 1], camera_axes[2, 1],
                     color='lightgreen', arrow_length_ratio=0.2, linewidth=2,
                     linestyle='--', alpha=0.7, label='Cam Y')
            ax.quiver(translation[0], translation[1], translation[2],
                     camera_axes[0, 2], camera_axes[1, 2], camera_axes[2, 2],
                     color='lightblue', arrow_length_ratio=0.2, linewidth=2,
                     linestyle='--', alpha=0.7, label='Cam Z')
        
        # 绘制车辆轮廓
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
        from matplotlib.patches import Polygon
        from mpl_toolkits.mplot3d.art3d import Poly3DCollection
        verts = [car_corners[:-1]]
        poly = Poly3DCollection(verts, alpha=0.2, facecolor='gray', edgecolor='black')
        ax.add_collection3d(poly)
        
        # 后轴标记
        ax.scatter(0, 0, 0, c='black', s=100, marker='o', label='Rear Axle Center')
        
        # 设置标签
        ax.set_xlabel('X (Forward) [m]', fontsize=11, fontweight='bold')
        ax.set_ylabel('Y (Left) [m]', fontsize=11, fontweight='bold')
        ax.set_zlabel('Z (Up) [m]', fontsize=11, fontweight='bold')
        ax.set_title('Camera Position in Vehicle Coordinate System (Interactive)', 
                    fontsize=13, fontweight='bold', pad=20)
        
        # 设置图例
        ax.legend(loc='upper left', fontsize=9, framealpha=0.9)
        
        # 设置坐标轴范围
        x_range = max(car_length, abs(translation[0]) + 1)
        y_range = max(car_width, abs(translation[1]) + 1)
        z_range = max(car_width/2, translation[2] + 1)
        
        ax.set_xlim([-x_range*0.2, x_range*1.1])
        ax.set_ylim([-y_range*1.2, y_range*1.2])
        ax.set_zlim([-0.5, z_range*1.2])
        
        ax.set_box_aspect([1, 1, 0.8])
        ax.grid(True, alpha=0.3)
        
        # 设置视角
        ax.view_init(elev=elev, azim=azim)
        
        return ax
    
    # 初始绘制
    current_elev = 25
    current_azim = 45
    draw_scene(current_elev, current_azim)
    
    # 添加说明文字
    info_text = (
        "Interactive 3D Visualization\n"
        "• Left Mouse: Rotate\n"
        "• Right Mouse: Pan\n"
        "• Scroll: Zoom\n"
        "• Press 'r': Reset view\n"
        "• Press 's': Save image\n"
        "• Press 'q': Quit"
    )
    fig.text(0.02, 0.98, info_text, transform=fig.transFigure,
            fontsize=9, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    # 添加键盘事件处理
    def on_key(event):
        if event.key == 'r':
            # 重置视角
            ax.view_init(elev=25, azim=45)
            plt.draw()
        elif event.key == 's':
            # 保存图像
            timestamp = __import__('datetime').datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f'camera_pose_3d_{timestamp}.png'
            plt.savefig(filename, dpi=150, bbox_inches='tight')
            print(f"✓ Saved: {filename}")
        elif event.key == 'q':
            # 退出
            plt.close()
    
    fig.canvas.mpl_connect('key_press_event', on_key)
    
    # 动画功能（可选）
    if enable_animation:
        import matplotlib.animation as animation
        
        def animate(frame):
            azim = (frame * 2) % 360  # 每帧旋转2度
            draw_scene(elev=25, azim=azim)
            return ax,
        
        anim = animation.FuncAnimation(fig, animate, frames=180, 
                                      interval=50, blit=False)
    
    plt.tight_layout()
    
    try:
        plt.show()
        return True
    except Exception as e:
        print(f"Error displaying interactive 3D plot: {e}")
        print("Your environment may not support GUI display.")
        return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='实时3D可视化相机位置')
    parser.add_argument('--extrinsic', type=str, default='config/extrinsic.yaml',
                       help='外参文件路径')
    parser.add_argument('--position', type=float, nargs=3,
                       help='直接指定相机位置 (x y z)')
    parser.add_argument('--orientation', type=float, nargs=3,
                       help='直接指定相机姿态 (roll pitch yaw)')
    parser.add_argument('--car-length', type=float, default=4.0,
                       help='车辆长度（米）')
    parser.add_argument('--car-width', type=float, default=2.0,
                       help='车辆宽度（米）')
    parser.add_argument('--hide-camera-frame', action='store_true',
                       help='隐藏相机坐标系')
    parser.add_argument('--animate', action='store_true',
                       help='启用自动旋转动画')
    args = parser.parse_args()
    
    print("\n" + "="*70)
    print("实时3D可视化 - 相机位置")
    print("="*70 + "\n")
    
    # 获取外参数据
    if args.position and args.orientation:
        # 使用命令行参数
        from src.calibration import ExtrinsicCalibration
        
        print("使用命令行参数创建外参...")
        print(f"位置: {args.position}")
        print(f"姿态: {args.orientation}")
        
        calibrator = ExtrinsicCalibration()
        extrinsic_data = calibrator.from_manual_measurement(
            position=tuple(args.position),
            orientation=tuple(args.orientation),
            angle_unit='degree'
        )
    else:
        # 从文件加载
        from src.utils import load_calibration
        
        if not os.path.exists(args.extrinsic):
            print(f"错误: 外参文件不存在: {args.extrinsic}")
            print("\n请使用以下方式之一:")
            print("1. 指定已有的外参文件:")
            print(f"   python {sys.argv[0]} --extrinsic config/extrinsic.yaml")
            print("\n2. 直接指定位置和姿态:")
            print(f"   python {sys.argv[0]} --position 1.5 0.0 1.8 --orientation 0.0 -10.0 0.0")
            return
        
        print(f"从文件加载外参: {args.extrinsic}")
        extrinsic_data = load_calibration(args.extrinsic)
        
        # 修复：检查是否包含顶层 'extrinsic' 键
        if 'extrinsic' in extrinsic_data:
            extrinsic_data = extrinsic_data['extrinsic']
    
    # 显示外参信息
    print("\n外参信息:")
    translation = np.array(extrinsic_data['translation_vector'])
    print(f"  位置: ({translation[0]:.2f}, {translation[1]:.2f}, {translation[2]:.2f}) m")
    
    if 'euler_angles' in extrinsic_data:
        euler = extrinsic_data['euler_angles']
        print(f"  姿态: roll={euler['roll']:.1f}°, pitch={euler['pitch']:.1f}°, yaw={euler['yaw']:.1f}°")
    
    print("\n" + "="*70)
    print("启动交互式3D可视化...")
    print("="*70)
    print("\n操作说明:")
    print("  • 鼠标左键拖动: 旋转视角")
    print("  • 鼠标右键拖动: 平移视图")
    print("  • 鼠标滚轮: 缩放")
    print("  • 按 'r' 键: 重置视角")
    print("  • 按 's' 键: 保存当前图像")
    print("  • 按 'q' 键: 退出")
    
    if args.animate:
        print("  • 自动旋转动画已启用")
    
    print("\n")
    
    # 显示3D可视化
    success = plot_camera_pose_3d_interactive(
        extrinsic_data=extrinsic_data,
        show_camera_frame=not args.hide_camera_frame,
        car_length=args.car_length,
        car_width=args.car_width,
        enable_animation=args.animate
    )
    
    if success:
        print("\n✓ 3D可视化已关闭")
    else:
        print("\n✗ 无法启动交互式3D显示")
        print("  您的环境可能不支持GUI显示")
        print("  建议在本地机器上运行，或使用保存到文件的方式")


if __name__ == '__main__':
    main()
