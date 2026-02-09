#!/usr/bin/env python3
"""
验证标定结果
检查标定的准确性
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import argparse
import cv2
import numpy as np
from src.calibration import ExtrinsicCalibration
from src.utils import load_calibration, visualize_calibration, plot_camera_pose_3d
from src.camera import FemtoBoltCamera


def main():
    parser = argparse.ArgumentParser(description='验证标定结果')
    parser.add_argument('--intrinsic', type=str, default='config/intrinsic.yaml',
                       help='内参文件路径')
    parser.add_argument('--extrinsic', type=str, default='config/extrinsic.yaml',
                       help='外参文件路径')
    parser.add_argument('--test-image', type=str,
                       help='测试图像路径（可选）')
    parser.add_argument('--live', action='store_true',
                       help='使用实时相机进行测试')
    args = parser.parse_args()
    
    print("\n" + "="*60)
    print("标定结果验证")
    print("="*60 + "\n")
    
    # 加载标定结果
    print("加载标定结果...")
    
    intrinsic_data = None
    if os.path.exists(args.intrinsic):
        intrinsic_data = load_calibration(args.intrinsic)
        print(f"✓ 内参已加载: {args.intrinsic}")
    else:
        print(f"✗ 内参文件不存在: {args.intrinsic}")
    
    extrinsic_data = None
    if os.path.exists(args.extrinsic):
        extrinsic_data = load_calibration(args.extrinsic)
        print(f"✓ 外参已加载: {args.extrinsic}")
    else:
        print(f"✗ 外参文件不存在: {args.extrinsic}")
    
    if intrinsic_data is None and extrinsic_data is None:
        print("\n错误: 至少需要提供一个标定文件")
        return
    
    # 显示标定结果
    print("\n")
    visualize_calibration(intrinsic_data or {}, extrinsic_data)
    
    # 3D可视化外参
    if extrinsic_data is not None:
        print("\n生成3D可视化...")
        plot_camera_pose_3d(extrinsic_data, save_path='verification_3d.png')
    
    # 测试去畸变
    if intrinsic_data is not None:
        print("\n" + "="*60)
        print("测试去畸变")
        print("="*60)
        
        camera_matrix = np.array(intrinsic_data['camera_matrix'])
        dist_coeffs = np.array(intrinsic_data['distortion_coeffs'])
        
        if args.test_image and os.path.exists(args.test_image):
            # 使用测试图像
            print(f"\n使用测试图像: {args.test_image}")
            image = cv2.imread(args.test_image)
            
            if image is not None:
                h, w = image.shape[:2]
                new_camera_matrix, roi = cv2.getOptimalNewCameraMatrix(
                    camera_matrix, dist_coeffs, (w, h), 1, (w, h)
                )
                undistorted = cv2.undistort(image, camera_matrix, dist_coeffs, 
                                           None, new_camera_matrix)
                
                cv2.imshow('原始图像', image)
                cv2.imshow('去畸变图像', undistorted)
                print("按任意键继续...")
                cv2.waitKey(0)
                cv2.destroyAllWindows()
        
        elif args.live:
            # 使用实时相机
            print("\n启动实时相机测试...")
            print("按 'q' 退出")
            
            camera = FemtoBoltCamera()
            if not camera.start():
                print("警告: 无法启动相机，使用模拟模式")
            
            try:
                while True:
                    color_image, _ = camera.get_frames()
                    
                    if color_image is None:
                        break
                    
                    h, w = color_image.shape[:2]
                    new_camera_matrix, roi = cv2.getOptimalNewCameraMatrix(
                        camera_matrix, dist_coeffs, (w, h), 1, (w, h)
                    )
                    undistorted = cv2.undistort(color_image, camera_matrix, 
                                               dist_coeffs, None, new_camera_matrix)
                    
                    # 并排显示
                    combined = np.hstack([color_image, undistorted])
                    cv2.putText(combined, "Original", (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    cv2.putText(combined, "Undistorted", (w + 10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    
                    cv2.imshow('去畸变测试', combined)
                    
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
            
            except KeyboardInterrupt:
                print("\n用户中断")
            
            finally:
                camera.stop()
                cv2.destroyAllWindows()
    
    # 测试坐标变换
    if extrinsic_data is not None:
        print("\n" + "="*60)
        print("坐标变换测试")
        print("="*60)
        
        calibrator = ExtrinsicCalibration()
        calibrator.load_from_dict(extrinsic_data)
        
        # 测试点
        test_points_camera = np.array([
            [0, 0, 1.0],    # 相机前方1米
            [0, 0, 2.0],    # 相机前方2米
            [0.5, 0, 1.0],  # 相机前方1米，右侧0.5米
            [-0.5, 0, 1.0], # 相机前方1米，左侧0.5米
        ])
        
        print("\n相机坐标系 -> 车辆坐标系:")
        print("-" * 60)
        print(f"{'相机坐标 (x, y, z)':<25} {'车辆坐标 (x, y, z)':<25}")
        print("-" * 60)
        
        for point_cam in test_points_camera:
            point_veh = calibrator.transform_point_to_vehicle(point_cam)
            print(f"({point_cam[0]:5.2f}, {point_cam[1]:5.2f}, {point_cam[2]:5.2f})     "
                  f"->  ({point_veh[0]:6.2f}, {point_veh[1]:6.2f}, {point_veh[2]:6.2f})")
        
        print("-" * 60)
    
    print("\n" + "="*60)
    print("验证完成")
    print("="*60 + "\n")


if __name__ == '__main__':
    main()
