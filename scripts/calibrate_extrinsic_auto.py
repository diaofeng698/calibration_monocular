#!/usr/bin/env python3
"""
自动外参标定
使用棋盘格标定板自动计算外参
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
                       help='棋盘格内角点数量 (列 行)')
    parser.add_argument('--square-size', type=float, default=0.025,
                       help='棋盘格方格大小(米)')
    parser.add_argument('--board-position', type=float, nargs=3, required=True,
                       help='标定板在车辆坐标系中的位置 (x y z) 单位:米')
    parser.add_argument('--board-orientation', type=float, nargs=3, default=[0, 0, 0],
                       help='标定板的姿态 (roll pitch yaw) 单位:度')
    args = parser.parse_args()
    
    print("\n" + "="*60)
    print("相机外参标定 - 自动标定方法")
    print("="*60)
    print(f"\n标定参数:")
    print(f"  棋盘格大小: {args.checkerboard[0]} x {args.checkerboard[1]}")
    print(f"  方格尺寸: {args.square_size} 米")
    print(f"  标定板位置: {args.board_position}")
    print(f"  标定板姿态: {args.board_orientation}")
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
            board_position=tuple(args.board_position),
            board_orientation=tuple(args.board_orientation)
        )
        
        # 可视化检测结果
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        ret, corners = cv2.findChessboardCorners(gray, tuple(args.checkerboard), None)
        
        if ret:
            img_with_corners = image.copy()
            cv2.drawChessboardCorners(img_with_corners, tuple(args.checkerboard), 
                                     corners, ret)
            # cv2.imshow('检测到的棋盘格', img_with_corners)
            # print("按任意键继续...")
            # cv2.waitKey(0)
            # cv2.destroyAllWindows()
        
        # 保存结果
        save_calibration(result, args.output)
        
        # 显示结果
        # print("\n")
        # visualize_calibration(intrinsic_data, result)
        
        # # 3D可视化
        # print("\n生成3D可视化...")
        # output_dir = os.path.dirname(args.output)
        # os.makedirs(output_dir, exist_ok=True)
        # viz_path = os.path.join(output_dir, 'camera_pose_3d.png')
        # try:
        #     plot_camera_pose_3d(result, save_path=viz_path)
        # except Exception as e:
        #     print(f"警告: 无法生成3D可视化 (可能是无GUI环境): {e}")
        #     print("跳过3D可视化...")
        
        print("\n✓ 外参标定完成!")
        print(f"结果已保存到: {args.output}")
        
    except ValueError as e:
        print(f"\n错误: {e}")
        print("请确保:")
        print("  1. 标定板在图像中完全可见")
        print("  2. 图像清晰，光照充足")
        print("  3. 棋盘格参数正确")


if __name__ == '__main__':
    main()
