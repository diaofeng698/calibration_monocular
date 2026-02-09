"""
可视化工具
用于显示标定结果
"""
import numpy as np
import cv2
import matplotlib
matplotlib.use('Agg')  # 使用非GUI后端
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


def draw_axes(image, camera_matrix, dist_coeffs, rvec, tvec, length=0.1):
    """
    在图像上绘制坐标轴
    
    Args:
        image: 输入图像
        camera_matrix: 相机内参矩阵
        dist_coeffs: 畸变系数
        rvec: 旋转向量
        tvec: 平移向量
        length: 坐标轴长度（米）
        
    Returns:
        绘制了坐标轴的图像
    """
    # 定义3D坐标轴点
    axis_points = np.float32([
        [0, 0, 0],           # 原点
        [length, 0, 0],      # X轴（红色）
        [0, length, 0],      # Y轴（绿色）
        [0, 0, length]       # Z轴（蓝色）
    ])
    
    # 投影到图像平面
    imgpts, _ = cv2.projectPoints(axis_points, rvec, tvec, camera_matrix, dist_coeffs)
    imgpts = imgpts.reshape(-1, 2).astype(int)
    
    origin = tuple(imgpts[0])
    
    # 绘制坐标轴
    img_with_axes = image.copy()
    img_with_axes = cv2.line(img_with_axes, origin, tuple(imgpts[1]), (0, 0, 255), 3)  # X轴-红色
    img_with_axes = cv2.line(img_with_axes, origin, tuple(imgpts[2]), (0, 255, 0), 3)  # Y轴-绿色
    img_with_axes = cv2.line(img_with_axes, origin, tuple(imgpts[3]), (255, 0, 0), 3)  # Z轴-蓝色
    
    return img_with_axes


def visualize_calibration(intrinsic_data: dict, extrinsic_data: dict = None):
    """
    可视化标定结果
    
    Args:
        intrinsic_data: 内参标定结果
        extrinsic_data: 外参标定结果（可选）
    """
    print("\n" + "="*60)
    print("标定结果")
    print("="*60)
    
    # 显示内参
    if intrinsic_data and 'camera_matrix' in intrinsic_data:
        print("\n【相机内参】")
        camera_matrix = np.array(intrinsic_data['camera_matrix'])
        print(f"相机矩阵:\n{camera_matrix}")
        print(f"\n焦距:")
        print(f"  fx = {camera_matrix[0, 0]:.2f} pixels")
        print(f"  fy = {camera_matrix[1, 1]:.2f} pixels")
        print(f"\n主点:")
        print(f"  cx = {camera_matrix[0, 2]:.2f} pixels")
        print(f"  cy = {camera_matrix[1, 2]:.2f} pixels")
        
        if 'distortion_coeffs' in intrinsic_data:
            dist_coeffs = np.array(intrinsic_data['distortion_coeffs'])
            print(f"\n畸变系数: {dist_coeffs.ravel()}")
        
        if 'rms_error' in intrinsic_data:
            print(f"\nRMS重投影误差: {intrinsic_data['rms_error']:.4f} pixels")
    
    # 显示外参
    if extrinsic_data is not None:
        print("\n【相机外参（相对于车辆后轴中心）】")
        
        translation = np.array(extrinsic_data['translation_vector'])
        print(f"\n位置 (x, y, z): ({translation[0]:.3f}, {translation[1]:.3f}, {translation[2]:.3f}) 米")
        print(f"  x (向前): {translation[0]:.3f} 米")
        print(f"  y (向左): {translation[1]:.3f} 米")
        print(f"  z (向上): {translation[2]:.3f} 米")
        
        if 'euler_angles' in extrinsic_data:
            euler = extrinsic_data['euler_angles']
            print(f"\n姿态 (roll, pitch, yaw):")
            print(f"  roll  (绕X轴): {euler['roll']:.2f}°")
            print(f"  pitch (绕Y轴): {euler['pitch']:.2f}°")
            print(f"  yaw   (绕Z轴): {euler['yaw']:.2f}°")
        
        rotation_matrix = np.array(extrinsic_data['rotation_matrix'])
        print(f"\n旋转矩阵:\n{rotation_matrix}")
    
    print("\n" + "="*60)


def plot_camera_pose_3d(extrinsic_data: dict, save_path: str = None, show_camera_frame: bool = True, 
                       car_length: float = 4.0, car_width: float = 2.0):
    """
    3D可视化相机在车辆坐标系中的位置
    
    Args:
        extrinsic_data: 外参标定结果
        save_path: 保存图像路径（可选）
        show_camera_frame: 是否显示相机坐标系
        car_length: 车辆长度（米），默认4.0
        car_width: 车辆宽度（米），默认2.0
    """
    try:
        fig = plt.figure(figsize=(12, 9))
        ax = fig.add_subplot(111, projection='3d')
        
        # 获取相机位置
        translation = np.array(extrinsic_data['translation_vector'])
        rotation_matrix = np.array(extrinsic_data['rotation_matrix'])
        
        # 计算坐标轴长度（根据相机位置自适应）
        max_dist = max(abs(translation[0]), abs(translation[1]), abs(translation[2]), car_length)
        axis_length = max(2.0, max_dist * 0.3)
        
        # 绘制车辆坐标系（原点在后轴中心）
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
        
        # 绘制相机坐标系（可选）
        if show_camera_frame:
            camera_axis_length = axis_length * 0.4
            camera_axes = rotation_matrix * camera_axis_length
            
            # 相机坐标系的三个轴（用浅色表示）
            ax.quiver(translation[0], translation[1], translation[2],
                     camera_axes[0, 0], camera_axes[1, 0], camera_axes[2, 0],
                     color='lightcoral', arrow_length_ratio=0.2, linewidth=2,
                     linestyle='--', alpha=0.7)
            ax.quiver(translation[0], translation[1], translation[2],
                     camera_axes[0, 1], camera_axes[1, 1], camera_axes[2, 1],
                     color='lightgreen', arrow_length_ratio=0.2, linewidth=2,
                     linestyle='--', alpha=0.7)
            ax.quiver(translation[0], translation[1], translation[2],
                     camera_axes[0, 2], camera_axes[1, 2], camera_axes[2, 2],
                     color='lightblue', arrow_length_ratio=0.2, linewidth=2,
                     linestyle='--', alpha=0.7)
        
        # 绘制车辆轮廓（俯视图）
        car_corners = np.array([
            [0, -car_width/2, 0],
            [car_length, -car_width/2, 0],
            [car_length, car_width/2, 0],
            [0, car_width/2, 0],
            [0, -car_width/2, 0]
        ])
        ax.plot(car_corners[:, 0], car_corners[:, 1], car_corners[:, 2], 
               'k-', linewidth=3, label='Vehicle', alpha=0.8)
        
        # 填充车辆底部（增强可视化）
        from matplotlib.patches import Polygon
        from mpl_toolkits.mplot3d.art3d import Poly3DCollection
        verts = [car_corners[:-1]]  # 移除重复的最后一个点
        poly = Poly3DCollection(verts, alpha=0.2, facecolor='gray', edgecolor='black')
        ax.add_collection3d(poly)
        
        # 添加后轴标记
        ax.scatter(0, 0, 0, c='black', s=100, marker='o', label='Rear Axle Center')
        
        # 设置标签和标题
        ax.set_xlabel('X (Forward) [m]', fontsize=11, fontweight='bold')
        ax.set_ylabel('Y (Left) [m]', fontsize=11, fontweight='bold')
        ax.set_zlabel('Z (Up) [m]', fontsize=11, fontweight='bold')
        ax.set_title('Camera Position in Vehicle Coordinate System', 
                    fontsize=13, fontweight='bold', pad=20)
        
        # 设置图例
        ax.legend(loc='upper left', fontsize=10, framealpha=0.9)
        
        # 设置坐标轴范围（自适应）
        x_range = max(car_length, abs(translation[0]) + 1)
        y_range = max(car_width, abs(translation[1]) + 1)
        z_range = max(car_width/2, translation[2] + 1)
        
        ax.set_xlim([-x_range*0.2, x_range*1.1])
        ax.set_ylim([-y_range*1.2, y_range*1.2])
        ax.set_zlim([-0.5, z_range*1.2])
        
        # 设置等比例显示
        ax.set_box_aspect([1, 1, 0.8])
        
        # 设置网格
        ax.grid(True, alpha=0.3)
        
        # 设置视角（从斜上方观看）
        ax.view_init(elev=25, azim=45)
        
        plt.tight_layout()
        
        # 保存或显示图像
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight', facecolor='white')
            print(f"3D visualization saved to: {save_path}")
            plt.close(fig)
            return True
        else:
            # 仅在GUI后端时尝试显示
            backend = matplotlib.get_backend().lower()
            if backend != 'agg':
                plt.show()
                return True
            else:
                print("Warning: Non-GUI backend (Agg) detected. Please specify save_path to save the figure.")
                plt.close(fig)
                return False
                
    except Exception as e:
        print(f"Error creating 3D visualization: {e}")
        if 'fig' in locals():
            plt.close(fig)
        return False


def visualize_undistortion(original_image, undistorted_image):
    """
    可视化畸变校正效果
    
    Args:
        original_image: 原始图像
        undistorted_image: 去畸变后的图像
    """
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    
    axes[0].imshow(cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB))
    axes[0].set_title('原始图像')
    axes[0].axis('off')
    
    axes[1].imshow(cv2.cvtColor(undistorted_image, cv2.COLOR_BGR2RGB))
    axes[1].set_title('去畸变图像')
    axes[1].axis('off')
    
    plt.tight_layout()
    plt.show()
