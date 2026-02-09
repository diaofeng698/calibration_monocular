#!/usr/bin/env python3
"""
实时使用标定参数示例
展示如何在实时应用中使用标定结果
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import cv2
import numpy as np
from src.camera import FemtoBoltCamera
from src.calibration import ExtrinsicCalibration
from src.utils import load_calibration


class CalibratedCamera:
    """带标定参数的相机类"""
    
    def __init__(self, intrinsic_file, extrinsic_file):
        """
        初始化
        
        Args:
            intrinsic_file: 内参文件路径
            extrinsic_file: 外参文件路径
        """
        # 加载内参
        intrinsic_data = load_calibration(intrinsic_file)
        self.camera_matrix = np.array(intrinsic_data['camera_matrix'])
        self.dist_coeffs = np.array(intrinsic_data['distortion_coeffs'])
        
        # 加载外参
        extrinsic_data = load_calibration(extrinsic_file)
        self.extrinsic = ExtrinsicCalibration()
        self.extrinsic.load_from_dict(extrinsic_data)
        
        # 初始化相机
        self.camera = FemtoBoltCamera()
        
        print("标定相机已初始化")
        print(f"内参: {intrinsic_file}")
        print(f"外参: {extrinsic_file}")
    
    def start(self):
        """启动相机"""
        return self.camera.start()
    
    def stop(self):
        """停止相机"""
        self.camera.stop()
    
    def get_frames(self):
        """获取图像帧"""
        return self.camera.get_frames()
    
    def undistort(self, image):
        """
        去畸变
        
        Args:
            image: 输入图像
            
        Returns:
            去畸变后的图像
        """
        h, w = image.shape[:2]
        new_camera_matrix, roi = cv2.getOptimalNewCameraMatrix(
            self.camera_matrix, self.dist_coeffs, (w, h), 1, (w, h)
        )
        undistorted = cv2.undistort(image, self.camera_matrix, 
                                    self.dist_coeffs, None, new_camera_matrix)
        return undistorted
    
    def pixel_to_camera(self, u, v, depth):
        """
        像素坐标转相机坐标
        
        Args:
            u, v: 像素坐标
            depth: 深度值（米）
            
        Returns:
            相机坐标系中的3D点
        """
        x = (u - self.camera_matrix[0, 2]) * depth / self.camera_matrix[0, 0]
        y = (v - self.camera_matrix[1, 2]) * depth / self.camera_matrix[1, 1]
        z = depth
        return np.array([x, y, z])
    
    def pixel_to_vehicle(self, u, v, depth):
        """
        像素坐标转车辆坐标
        
        Args:
            u, v: 像素坐标
            depth: 深度值（米）
            
        Returns:
            车辆坐标系中的3D点
        """
        point_camera = self.pixel_to_camera(u, v, depth)
        return self.extrinsic.transform_point_to_vehicle(point_camera)
    
    def camera_to_vehicle(self, point_camera):
        """
        相机坐标转车辆坐标
        
        Args:
            point_camera: 相机坐标系中的点
            
        Returns:
            车辆坐标系中的点
        """
        return self.extrinsic.transform_point_to_vehicle(point_camera)


def main():
    """实时演示示例"""
    print("\n" + "="*60)
    print("实时标定参数使用示例")
    print("="*60 + "\n")
    
    # 检查标定文件
    intrinsic_file = 'config/intrinsic.yaml'
    extrinsic_file = 'config/extrinsic.yaml'
    
    if not os.path.exists(intrinsic_file):
        print(f"内参文件不存在: {intrinsic_file}")
        print("使用示例文件...")
        intrinsic_file = 'config/intrinsic_example.yaml'
    
    if not os.path.exists(extrinsic_file):
        print(f"外参文件不存在: {extrinsic_file}")
        print("使用示例文件...")
        extrinsic_file = 'config/extrinsic_example.yaml'
    
    # 初始化标定相机
    cam = CalibratedCamera(intrinsic_file, extrinsic_file)
    
    if not cam.start():
        print("警告: 无法启动相机，使用模拟模式")
    
    print("\n操作说明:")
    print("  - 点击图像选择一个点")
    print("  - 按 'q' 退出")
    print("  - 按 's' 保存当前帧")
    print()
    
    # 鼠标回调
    selected_point = None
    
    def mouse_callback(event, x, y, flags, param):
        nonlocal selected_point
        if event == cv2.EVENT_LBUTTONDOWN:
            selected_point = (x, y)
    
    cv2.namedWindow('标定相机')
    cv2.setMouseCallback('标定相机', mouse_callback)
    
    frame_count = 0
    
    try:
        while True:
            # 获取图像
            color_image, depth_image = cam.get_frames()
            
            if color_image is None:
                break
            
            # 去畸变
            undistorted = cam.undistort(color_image)
            
            # 显示信息
            display = undistorted.copy()
            
            # 如果选择了点，显示坐标转换
            if selected_point is not None:
                u, v = selected_point
                
                # 绘制选中点
                cv2.circle(display, (u, v), 5, (0, 255, 0), -1)
                cv2.circle(display, (u, v), 10, (0, 255, 0), 2)
                
                # 假设深度为2米（实际应从深度图获取）
                depth = 2.0
                
                # 坐标转换
                point_camera = cam.pixel_to_camera(u, v, depth)
                point_vehicle = cam.pixel_to_vehicle(u, v, depth)
                
                # 显示坐标信息
                info_y = 30
                cv2.putText(display, f"Pixel: ({u}, {v})", 
                           (10, info_y), cv2.FONT_HERSHEY_SIMPLEX, 
                           0.6, (255, 255, 255), 2)
                info_y += 25
                
                cv2.putText(display, f"Camera: ({point_camera[0]:.2f}, "
                           f"{point_camera[1]:.2f}, {point_camera[2]:.2f})m", 
                           (10, info_y), cv2.FONT_HERSHEY_SIMPLEX, 
                           0.6, (255, 255, 255), 2)
                info_y += 25
                
                cv2.putText(display, f"Vehicle: ({point_vehicle[0]:.2f}, "
                           f"{point_vehicle[1]:.2f}, {point_vehicle[2]:.2f})m", 
                           (10, info_y), cv2.FONT_HERSHEY_SIMPLEX, 
                           0.6, (255, 255, 255), 2)
            
            # 显示帧数
            cv2.putText(display, f"Frame: {frame_count}", 
                       (display.shape[1] - 150, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            cv2.imshow('标定相机', display)
            
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                break
            elif key == ord('s'):
                filename = f"frame_{frame_count:04d}.png"
                cv2.imwrite(filename, display)
                print(f"已保存: {filename}")
            
            frame_count += 1
    
    except KeyboardInterrupt:
        print("\n用户中断")
    
    finally:
        cam.stop()
        cv2.destroyAllWindows()
    
    print("\n程序结束")


if __name__ == '__main__':
    main()
