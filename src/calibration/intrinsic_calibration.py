"""
相机内参标定
使用棋盘格标定法
"""
import numpy as np
import cv2
import os
from typing import List, Tuple, Optional


class IntrinsicCalibration:
    """相机内参标定类"""
    
    def __init__(self, checkerboard_size=(9, 6), square_size=0.025):
        """
        初始化标定器
        
        Args:
            checkerboard_size: 棋盘格内角点数量 (cols, rows)
            square_size: 棋盘格方格大小(米)
        """
        self.checkerboard_size = checkerboard_size
        self.square_size = square_size
        
        # 3D点（棋盘格在世界坐标系中的位置）
        self.objp = np.zeros((checkerboard_size[0] * checkerboard_size[1], 3), np.float32)
        self.objp[:, :2] = np.mgrid[0:checkerboard_size[0], 
                                     0:checkerboard_size[1]].T.reshape(-1, 2)
        self.objp *= square_size
        
        # 存储所有图像的3D点和2D点
        self.objpoints = []  # 3D点
        self.imgpoints = []  # 2D点
        
        # 标定结果
        self.camera_matrix = None
        self.dist_coeffs = None
        self.rvecs = None
        self.tvecs = None
        self.rms_error = None
    
    def find_corners(self, image: np.ndarray, show=False) -> Optional[np.ndarray]:
        """
        在图像中查找棋盘格角点
        
        Args:
            image: 输入图像（BGR或灰度）
            show: 是否显示检测结果
            
        Returns:
            角点坐标数组，如果未找到返回None
        """
        # 转换为灰度图
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # 查找棋盘格角点
        ret, corners = cv2.findChessboardCorners(
            gray, 
            self.checkerboard_size,
            cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_NORMALIZE_IMAGE
        )
        
        if ret:
            # 亚像素精确化
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
            corners = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
            
            if show:
                img_with_corners = image.copy()
                cv2.drawChessboardCorners(img_with_corners, self.checkerboard_size, 
                                         corners, ret)
                cv2.imshow('Corners', img_with_corners)
                cv2.waitKey(500)
            
            return corners
        
        return None
    
    def add_image(self, image: np.ndarray) -> bool:
        """
        添加一张标定图像
        
        Args:
            image: 输入图像
            
        Returns:
            是否成功找到角点
        """
        corners = self.find_corners(image)
        
        if corners is not None:
            self.objpoints.append(self.objp)
            self.imgpoints.append(corners)
            return True
        
        return False
    
    def calibrate(self, image_size: Tuple[int, int]) -> dict:
        """
        执行标定计算
        
        Args:
            image_size: 图像尺寸 (width, height)
            
        Returns:
            包含标定结果的字典
        """
        if len(self.objpoints) < 3:
            raise ValueError(f"需要至少3张图像进行标定，当前只有{len(self.objpoints)}张")
        
        print(f"使用 {len(self.objpoints)} 张图像进行标定...")
        
        # 执行标定
        ret, camera_matrix, dist_coeffs, rvecs, tvecs = cv2.calibrateCamera(
            self.objpoints,
            self.imgpoints,
            image_size,
            None,
            None
        )
        
        self.camera_matrix = camera_matrix
        self.dist_coeffs = dist_coeffs
        self.rvecs = rvecs
        self.tvecs = tvecs
        self.rms_error = ret
        
        print(f"标定完成！RMS误差: {ret:.4f}")
        print(f"相机内参矩阵:\n{camera_matrix}")
        print(f"畸变系数: {dist_coeffs.ravel()}")
        
        return {
            'camera_matrix': camera_matrix,
            'distortion_coeffs': dist_coeffs,
            'rms_error': ret,
            'image_width': image_size[0],
            'image_height': image_size[1]
        }
    
    def load_images_from_folder(self, folder_path: str) -> int:
        """
        从文件夹加载所有标定图像
        
        Args:
            folder_path: 图像文件夹路径
            
        Returns:
            成功加载的图像数量
        """
        if not os.path.exists(folder_path):
            raise FileNotFoundError(f"文件夹不存在: {folder_path}")
        
        success_count = 0
        image_files = sorted([f for f in os.listdir(folder_path) 
                             if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))])
        
        print(f"在文件夹中找到 {len(image_files)} 张图像")
        
        for img_file in image_files:
            img_path = os.path.join(folder_path, img_file)
            image = cv2.imread(img_path)
            
            if image is None:
                print(f"无法读取图像: {img_file}")
                continue
            
            if self.add_image(image):
                print(f"✓ {img_file}: 找到角点")
                success_count += 1
            else:
                print(f"✗ {img_file}: 未找到角点，已删除")
                os.remove(img_path)
        
        print(f"\n成功处理 {success_count}/{len(image_files)} 张图像")
        return success_count
    
    def undistort_image(self, image: np.ndarray) -> np.ndarray:
        """
        去畸变图像
        
        Args:
            image: 输入图像
            
        Returns:
            去畸变后的图像
        """
        if self.camera_matrix is None or self.dist_coeffs is None:
            raise ValueError("请先进行标定")
        
        h, w = image.shape[:2]
        new_camera_matrix, roi = cv2.getOptimalNewCameraMatrix(
            self.camera_matrix, self.dist_coeffs, (w, h), 1, (w, h)
        )
        
        undistorted = cv2.undistort(image, self.camera_matrix, self.dist_coeffs, 
                                    None, new_camera_matrix)
        
        # 裁剪图像
        x, y, w, h = roi
        undistorted = undistorted[y:y+h, x:x+w]
        
        return undistorted
    
    def calculate_reprojection_error(self) -> float:
        """
        计算重投影误差
        
        Returns:
            平均重投影误差
        """
        if self.camera_matrix is None:
            raise ValueError("请先进行标定")
        
        total_error = 0
        for i in range(len(self.objpoints)):
            imgpoints2, _ = cv2.projectPoints(
                self.objpoints[i], self.rvecs[i], self.tvecs[i],
                self.camera_matrix, self.dist_coeffs
            )
            error = cv2.norm(self.imgpoints[i], imgpoints2, cv2.NORM_L2) / len(imgpoints2)
            total_error += error
        
        mean_error = total_error / len(self.objpoints)
        return mean_error
