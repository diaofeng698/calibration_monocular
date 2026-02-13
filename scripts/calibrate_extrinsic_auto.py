#!/usr/bin/env python3
"""
自动外参标定
使用棋盘格标定板自动计算外参

坐标系定义:
1. 棋盘格坐标系: 左上角角点为原点, X轴水平向右, Y轴垂直向下, Z轴向外(垂直棋盘格平面)
2. 车辆坐标系: 后轴中心为原点, X轴向前(车头方向), Y轴向左, Z轴向上
3. 相机坐标系: 相机光心为原点, X轴向右, Y轴向下, Z轴向前(光轴方向)

标定目标: 计算相机相对车辆后轴中心的外参矩阵(旋转+平移)
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import argparse
import cv2
import numpy as np
from src.calibration import ExtrinsicCalibration
from src.utils import save_calibration, load_calibration, visualize_calibration, plot_camera_pose_3d


def main():
    parser = argparse.ArgumentParser(description='自动外参标定')
    parser.add_argument('--intrinsic', type=str, required=True,
                       help='内参文件路径')
    parser.add_argument('--image', type=str, required=True,
                       help='包含标定板的图像路径')
    parser.add_argument('--output', type=str, default='config/extrinsic.yaml',
                       help='输出文件路径')
    parser.add_argument('--checkerboard', type=int, nargs=2, default=[12, 8],
                       help='棋盘格内角点数量 (列 行) - 对应X轴和Y轴方向')
    parser.add_argument('--square-size', type=float, default=0.038,
                       help='棋盘格方格大小(米)')
    parser.add_argument('--board-to-vehicle', type=float, nargs=6, required=True,
                       help='棋盘格左上角在车辆坐标系中的位置和姿态 (x y z roll pitch yaw) 单位:米和度')
    parser.add_argument('--rear-axle-offset', type=float, nargs=3, default=[0, 0, 0],
                       help='相机安装位置相对后轴中心的粗略偏移 (x y z) 单位:米, 用于初始估计')
    parser.add_argument('--fisheye', action='store_true', default=True,
                       help='使用鱼眼相机模型 (默认: True)')
    parser.add_argument('--no-fisheye', action='store_false', dest='fisheye',
                       help='使用标准针孔相机模型')
    args = parser.parse_args()
    
    print("\n" + "="*60)
    print("相机外参标定 - 自动标定方法")
    print("="*60)
    print(f"\n坐标系定义:")
    print(f"  棋盘格坐标系: 左上角为原点, X右 Y下 Z外")
    print(f"  车辆坐标系: 后轴中心为原点, X前 Y左 Z上")
    print(f"  相机坐标系: 光心为原点, X右 Y下 Z前")
    print(f"\n标定参数:")
    print(f"  相机模型: {'鱼眼相机' if args.fisheye else '标准针孔相机'}")
    print(f"  棋盘格大小: {args.checkerboard[0]}x{args.checkerboard[1]} (列x行)")
    print(f"  方格尺寸: {args.square_size} 米")
    print(f"  棋盘格到车辆: 位置{args.board_to_vehicle[:3]}, 姿态{args.board_to_vehicle[3:]}度")
    print(f"  后轴偏移估计: {args.rear_axle_offset}")
    print("="*60 + "\n")
    
    # 加载内参
    print("加载相机内参...")
    intrinsic_data = load_calibration(args.intrinsic)
    camera_matrix = np.array(intrinsic_data['camera_matrix'])
    dist_coeffs = np.array(intrinsic_data['distortion_coeffs'])
    
    # 读取图像
    print("读取标定图像...")
    image = cv2.imread(args.image)
    if image is None:
        print(f"错误: 无法读取图像 {args.image}")
        return
    
    # 执行标定
    print("检测标定板...")
    calibrator = ExtrinsicCalibration()
    
    try:
        result = calibrator.from_checkerboard(
            image=image,
            camera_matrix=camera_matrix,
            dist_coeffs=dist_coeffs,
            checkerboard_size=tuple(args.checkerboard),
            square_size=args.square_size,
            board_to_vehicle_pose=args.board_to_vehicle,
            rear_axle_offset=args.rear_axle_offset,
            use_fisheye=args.fisheye
        )
        
        # 可视化检测结果
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        ret, corners = cv2.findChessboardCorners(gray, tuple(args.checkerboard), None)
        
        if ret:
            img_with_corners = image.copy()
            cv2.drawChessboardCorners(img_with_corners, tuple(args.checkerboard), 
                                     corners, ret)
            # 保存检测结果
            output_dir = os.path.dirname(args.output)
            os.makedirs(output_dir, exist_ok=True)
            detection_path = os.path.join(output_dir, 'checkerboard_detection.png')
            cv2.imwrite(detection_path, img_with_corners)
            print(f"  检测结果已保存: {detection_path}")
        
        # 保存结果
        save_calibration(result, args.output)
        
        # 显示结果
        print("\n")
        visualize_calibration(intrinsic_data, result)
        
        # 3D可视化
        print("\n生成3D可视化...")
        output_dir = os.path.dirname(args.output)
        os.makedirs(output_dir, exist_ok=True)
        viz_path = os.path.join(output_dir, 'camera_pose_3d.png')
        try:
            plot_camera_pose_3d(result, save_path=viz_path)
        except Exception as e:
            print(f"警告: 无法生成3D可视化 (可能是无GUI环境): {e}")
            print("跳过3D可视化...")
        
        print("\n✓ 外参标定完成!")
        print(f"结果已保存到: {args.output}")
        print(f"\n相机相对车辆后轴中心的外参:")
        print(f"  位置 (x,y,z): {result.get('translation', 'N/A')}")
        print(f"  姿态 (roll,pitch,yaw): {result.get('rotation_euler', 'N/A')}")
        
    except ValueError as e:
        print(f"\n错误: {e}")
        print("请确保:")
        print("  1. 标定板在图像中完全可见")
        print("  2. 图像清晰，光照充足")
        print("  3. 棋盘格参数正确")
        print("  4. 棋盘格到车辆的位姿参数正确")


if __name__ == '__main__':
    main()
