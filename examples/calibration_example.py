#!/usr/bin/env python3
"""
完整标定流程示例
演示从零开始完成内参和外参标定的完整流程
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import cv2
import numpy as np
from src.camera import FemtoBoltCamera
from src.calibration import IntrinsicCalibration, ExtrinsicCalibration
from src.utils import save_calibration, load_calibration, visualize_calibration


def example_intrinsic_calibration():
    """示例：内参标定流程"""
    print("\n" + "="*60)
    print("示例：内参标定")
    print("="*60 + "\n")
    
    # 1. 创建标定器
    calibrator = IntrinsicCalibration(
        checkerboard_size=(9, 6),  # 棋盘格内角点数量
        square_size=0.025           # 方格尺寸25mm
    )
    
    # 2. 加载标定图像
    image_folder = 'data/intrinsic_calibration'
    if os.path.exists(image_folder):
        success_count = calibrator.load_images_from_folder(image_folder)
        
        if success_count >= 10:
            # 3. 执行标定
            image_size = (640, 480)  # 根据实际图像设置
            result = calibrator.calibrate(image_size)
            
            # 4. 保存结果
            save_calibration(result, 'config/intrinsic.yaml')
            
            print("\n✓ 内参标定完成!")
        else:
            print(f"⚠ 只找到 {success_count} 张有效图像，建议至少10张")
    else:
        print(f"图像文件夹不存在: {image_folder}")
        print("请先使用 capture_calibration_images.py 采集标定图像")


def example_extrinsic_calibration_manual():
    """示例：手动测量外参标定"""
    print("\n" + "="*60)
    print("示例：手动外参标定")
    print("="*60 + "\n")
    
    # 创建标定器
    calibrator = ExtrinsicCalibration()
    
    # 手动测量的参数（示例值）
    # 假设相机安装在车顶中央，距离后轴1.5米，高度1.8米
    position = (1.5, 0.0, 1.8)  # (x, y, z) 单位：米
    orientation = (0.0, -10.0, 0.0)  # (roll, pitch, yaw) 单位：度
    # pitch = -10度表示相机向下倾斜10度
    
    # 设置外参
    result = calibrator.from_manual_measurement(
        position=position,
        orientation=orientation,
        angle_unit='degree'
    )
    
    # 保存结果
    save_calibration(result, 'config/extrinsic.yaml')
    
    print("\n✓ 外参标定完成!")
    
    # 测试坐标变换
    print("\n测试坐标变换:")
    point_camera = np.array([0, 0, 2.0])  # 相机前方2米
    point_vehicle = calibrator.transform_point_to_vehicle(point_camera)
    print(f"相机坐标: {point_camera}")
    print(f"车辆坐标: {point_vehicle}")


def example_extrinsic_calibration_auto():
    """示例：自动外参标定（使用标定板）"""
    print("\n" + "="*60)
    print("示例：自动外参标定")
    print("="*60 + "\n")
    
    # 1. 加载内参
    intrinsic_file = 'config/intrinsic.yaml'
    if not os.path.exists(intrinsic_file):
        print(f"内参文件不存在: {intrinsic_file}")
        print("请先完成内参标定")
        return
    
    intrinsic_data = load_calibration(intrinsic_file)
    camera_matrix = np.array(intrinsic_data['camera_matrix'])
    dist_coeffs = np.array(intrinsic_data['distortion_coeffs'])
    
    # 2. 准备标定
    calibrator = ExtrinsicCalibration()
    
    # 假设有一张包含标定板的图像
    image_path = 'data/extrinsic_calibration/board_image.jpg'
    if not os.path.exists(image_path):
        print(f"标定图像不存在: {image_path}")
        print("请拍摄一张包含标定板的图像")
        return
    
    image = cv2.imread(image_path)
    
    # 标定板在车辆坐标系中的位置（需要实际测量）
    # 例如：将标定板放在车辆前方1米，地面上
    board_position = (1.0, 0.0, 0.0)
    board_orientation = (0.0, 0.0, 0.0)  # 水平放置
    
    # 3. 执行标定
    result = calibrator.from_checkerboard(
        image=image,
        camera_matrix=camera_matrix,
        dist_coeffs=dist_coeffs,
        checkerboard_size=(9, 6),
        square_size=0.025,
        board_position=board_position,
        board_orientation=board_orientation
    )
    
    # 4. 保存结果
    save_calibration(result, 'config/extrinsic_auto.yaml')
    
    print("\n✓ 自动外参标定完成!")


def example_use_calibration():
    """示例：使用标定结果"""
    print("\n" + "="*60)
    print("示例：使用标定结果")
    print("="*60 + "\n")
    
    # 1. 加载标定结果
    intrinsic_data = load_calibration('config/intrinsic.yaml')
    extrinsic_data = load_calibration('config/extrinsic.yaml')
    
    camera_matrix = np.array(intrinsic_data['camera_matrix'])
    dist_coeffs = np.array(intrinsic_data['distortion_coeffs'])
    
    # 2. 设置外参标定器
    extrinsic_calib = ExtrinsicCalibration()
    extrinsic_calib.load_from_dict(extrinsic_data)
    
    # 3. 使用相机
    camera = FemtoBoltCamera()
    camera.start()
    
    try:
        # 获取一帧
        color_image, depth_image = camera.get_frames()
        
        if color_image is not None:
            # 去畸变
            h, w = color_image.shape[:2]
            new_camera_matrix, roi = cv2.getOptimalNewCameraMatrix(
                camera_matrix, dist_coeffs, (w, h), 1, (w, h)
            )
            undistorted = cv2.undistort(color_image, camera_matrix, 
                                       dist_coeffs, None, new_camera_matrix)
            
            # 示例：将图像中的某个像素坐标转换到车辆坐标系
            # （需要深度信息）
            pixel_u, pixel_v = 320, 240  # 图像中心
            depth = 2.0  # 假设深度2米
            
            # 像素坐标 -> 相机坐标
            x_cam = (pixel_u - camera_matrix[0, 2]) * depth / camera_matrix[0, 0]
            y_cam = (pixel_v - camera_matrix[1, 2]) * depth / camera_matrix[1, 1]
            z_cam = depth
            point_camera = np.array([x_cam, y_cam, z_cam])
            
            # 相机坐标 -> 车辆坐标
            point_vehicle = extrinsic_calib.transform_point_to_vehicle(point_camera)
            
            print(f"像素坐标: ({pixel_u}, {pixel_v})")
            print(f"相机坐标: {point_camera}")
            print(f"车辆坐标: {point_vehicle}")
    
    finally:
        camera.stop()


def main():
    """主函数：运行所有示例"""
    print("\n" + "="*70)
    print("Femto Bolt 相机标定 - 完整示例")
    print("="*70)
    
    print("\n选择要运行的示例:")
    print("1. 内参标定")
    print("2. 手动外参标定")
    print("3. 自动外参标定")
    print("4. 使用标定结果")
    print("5. 显示已有标定结果")
    print("0. 退出")
    
    choice = input("\n请输入选项 (0-5): ").strip()
    
    if choice == '1':
        example_intrinsic_calibration()
    elif choice == '2':
        example_extrinsic_calibration_manual()
    elif choice == '3':
        example_extrinsic_calibration_auto()
    elif choice == '4':
        example_use_calibration()
    elif choice == '5':
        # 显示已有的标定结果
        intrinsic_file = 'config/intrinsic.yaml'
        extrinsic_file = 'config/extrinsic.yaml'
        
        intrinsic_data = None
        extrinsic_data = None
        
        if os.path.exists(intrinsic_file):
            intrinsic_data = load_calibration(intrinsic_file)
        if os.path.exists(extrinsic_file):
            extrinsic_data = load_calibration(extrinsic_file)
        
        if intrinsic_data or extrinsic_data:
            visualize_calibration(intrinsic_data or {}, extrinsic_data)
        else:
            print("未找到标定文件")
    elif choice == '0':
        print("退出")
    else:
        print("无效选项")


if __name__ == '__main__':
    main()
