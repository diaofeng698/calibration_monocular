"""
相机外参标定
计算相机相对于汽车后轴中心的变换矩阵

坐标系定义:
1. 棋盘格坐标系: 左上角角点为原点, X轴水平向右, Y轴垂直向下, Z轴向外(垂直棋盘格平面)
2. 车辆坐标系: 后轴中心为原点, X轴向前(车头方向), Y轴向左, Z轴向上
3. 相机坐标系: 相机光心为原点, X轴向右, Y轴向下, Z轴向前(光轴方向)
"""
import numpy as np
import cv2
from typing import Tuple, Optional, Union, List
from transforms3d.euler import euler2mat, mat2euler


class ExtrinsicCalibration:
    """相机外参标定类"""
    
    def __init__(self):
        """初始化外参标定器"""
        self.rotation_matrix = None
        self.translation_vector = None
        self.transformation_matrix = None
    
    def from_manual_measurement(self, 
                                position: Tuple[float, float, float],
                                orientation: Tuple[float, float, float],
                                angle_unit='degree') -> dict:
        """
        通过手动测量设置外参
        
        Args:
            position: 相机在车辆坐标系中的位置 (x, y, z) 单位：米
                     x: 向前为正，y: 向左为正，z: 向上为正
            orientation: 相机的旋转角度 (roll, pitch, yaw)
                        roll: 绕X轴旋转，pitch: 绕Y轴旋转，yaw: 绕Z轴旋转
            angle_unit: 角度单位，'degree' 或 'radian'
            
        Returns:
            包含外参的字典
        """
        x, y, z = position
        roll, pitch, yaw = orientation
        
        # 转换为弧度
        if angle_unit == 'degree':
            roll = np.deg2rad(roll)
            pitch = np.deg2rad(pitch)
            yaw = np.deg2rad(yaw)
        
        # 计算旋转矩阵 (ZYX欧拉角)
        self.rotation_matrix = euler2mat(yaw, pitch, roll, 'szyx')
        
        # 设置平移向量
        self.translation_vector = np.array([x, y, z])
        
        # 构建4x4变换矩阵
        self.transformation_matrix = np.eye(4)
        self.transformation_matrix[:3, :3] = self.rotation_matrix
        self.transformation_matrix[:3, 3] = self.translation_vector
        
        print("外参设置完成（手动测量）:")
        print(f"位置 (x, y, z): {position}")
        print(f"姿态 (roll, pitch, yaw): {orientation} {angle_unit}")
        print(f"旋转矩阵:\n{self.rotation_matrix}")
        print(f"平移向量: {self.translation_vector}")
        
        return self.get_calibration_result()
    
    def from_pnp(self, 
                 object_points: np.ndarray,
                 image_points: np.ndarray,
                 camera_matrix: np.ndarray,
                 dist_coeffs: np.ndarray,
                 marker_to_vehicle_transform: np.ndarray,
                 use_fisheye: bool = True) -> dict:
        """
        通过PnP算法计算外参
        
        Args:
            object_points: 标定板上的3D点（标定板坐标系）
            image_points: 图像中对应的2D点
            camera_matrix: 相机内参矩阵
            dist_coeffs: 畸变系数
            marker_to_vehicle_transform: 标定板坐标系到车辆坐标系的变换矩阵 (4x4)
            use_fisheye: 是否使用鱼眼相机模型
            
        Returns:
            包含外参的字典
        """
        # 使用PnP求解相机位姿（相机到标定板）
        if use_fisheye:
            # 鱼眼相机需要特殊处理，先去畸变图像点
            # OpenCV的fisheye模块不直接提供solvePnP，需要使用undistortPoints
            image_points_undistorted = cv2.fisheye.undistortPoints(
                image_points, camera_matrix, dist_coeffs, P=camera_matrix
            )
            # 使用去畸变后的点和无畸变模型求解
            success, rvec, tvec = cv2.solvePnP(
                object_points,
                image_points_undistorted,
                camera_matrix,
                None,  # 已去畸变，不需要畸变系数
                flags=cv2.SOLVEPNP_ITERATIVE
            )
        else:
            # 标准相机模型
            success, rvec, tvec = cv2.solvePnP(
                object_points,
                image_points,
                camera_matrix,
                dist_coeffs,
                flags=cv2.SOLVEPNP_ITERATIVE
            )
        
        if not success:
            raise ValueError("PnP求解失败")
        
        # 转换旋转向量为旋转矩阵（相机到标定板）
        R_cam_to_board, _ = cv2.Rodrigues(rvec)
        t_cam_to_board = tvec.flatten()
        
        # 构建相机到标定板的变换矩阵
        T_cam_to_board = np.eye(4)
        T_cam_to_board[:3, :3] = R_cam_to_board
        T_cam_to_board[:3, 3] = t_cam_to_board
        
        # 计算标定板到相机的变换（求逆）
        T_board_to_cam = np.linalg.inv(T_cam_to_board)
        
        # 计算相机到车辆坐标系的变换
        # T_cam_to_vehicle = T_board_to_vehicle @ T_cam_to_board
        T_board_to_vehicle = marker_to_vehicle_transform
        T_cam_to_vehicle = T_board_to_vehicle @ T_board_to_cam
        
        # 提取旋转和平移
        self.rotation_matrix = T_cam_to_vehicle[:3, :3]
        self.translation_vector = T_cam_to_vehicle[:3, 3]
        self.transformation_matrix = T_cam_to_vehicle
        
        print("外参标定完成（PnP方法）:")
        print(f"旋转矩阵:\n{self.rotation_matrix}")
        print(f"平移向量: {self.translation_vector}")
        
        return self.get_calibration_result()
    
    def from_checkerboard(self,
                         image: np.ndarray,
                         camera_matrix: np.ndarray,
                         dist_coeffs: np.ndarray,
                         checkerboard_size: Tuple[int, int],
                         square_size: float,
                         board_to_vehicle_pose: Union[List[float], Tuple[float, ...]],
                         rear_axle_offset: Optional[Union[List[float], Tuple[float, ...]]] = None,
                         use_fisheye: bool = True) -> dict:
        """
        使用棋盘格自动标定外参
        
        坐标系说明:
        - 棋盘格坐标系: 左上角为原点, X轴向右, Y轴向下, Z轴向外
        - 车辆坐标系: 后轴中心为原点, X轴向前, Y轴向左, Z轴向上
        
        Args:
            image: 包含棋盘格的图像
            camera_matrix: 相机内参矩阵
            dist_coeffs: 畸变系数
            checkerboard_size: 棋盘格大小 (cols, rows) - 内角点数量
            square_size: 方格尺寸（米）
            board_to_vehicle_pose: 棋盘格左上角在车辆坐标系中的位姿 
                                   [x, y, z, roll, pitch, yaw] 
                                   位置单位:米, 姿态单位:度
            rear_axle_offset: 相机相对后轴的粗略偏移 (x, y, z) 米 (可选, 未使用)
            use_fisheye: 是否使用鱼眼相机模型 (默认: True)
            
        Returns:
            包含外参的字典
        """
        # 查找棋盘格角点
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        ret, corners = cv2.findChessboardCorners(gray, checkerboard_size, None)
        
        if not ret:
            raise ValueError("未在图像中找到棋盘格")
        
        # 亚像素精确化
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        corners = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
        
        # 生成3D点（棋盘格坐标系: 左上角为原点, X右, Y下, Z外）
        objp = np.zeros((checkerboard_size[0] * checkerboard_size[1], 3), np.float32)
        objp[:, :2] = np.mgrid[0:checkerboard_size[0], 
                               0:checkerboard_size[1]].T.reshape(-1, 2)
        objp *= square_size
        
        # 解析棋盘格到车辆的位姿
        board_position = board_to_vehicle_pose[:3]
        board_orientation = board_to_vehicle_pose[3:6]
        
        # 构建棋盘格到车辆坐标系的变换矩阵
        # 棋盘格坐标系: X右, Y下, Z外
        # 车辆坐标系: X前, Y左, Z上
        
        # 1. 先构建棋盘格姿态的旋转矩阵
        roll, pitch, yaw = [np.deg2rad(a) for a in board_orientation]
        R_board_orientation = euler2mat(yaw, pitch, roll, 'szyx')
        
        # 2. 棋盘格坐标系到车辆坐标系的基础变换（坐标轴对齐）
        # 棋盘格 X(右) -> 车辆 Y(左) 需要取反: -X_board = Y_vehicle
        # 棋盘格 Y(下) -> 车辆 Z(上) 需要取反: -Y_board = Z_vehicle  
        # 棋盘格 Z(外) -> 车辆 X(前): Z_board = X_vehicle
        R_board_to_vehicle_base = np.array([
            [0, 0, 1],    # 棋盘格Z -> 车辆X
            [-1, 0, 0],   # 棋盘格-X -> 车辆Y
            [0, -1, 0]    # 棋盘格-Y -> 车辆Z
        ])
        
        # 3. 组合旋转
        R_board_to_vehicle = R_board_orientation @ R_board_to_vehicle_base
        
        # 4. 构建完整的变换矩阵
        T_board_to_vehicle = np.eye(4)
        T_board_to_vehicle[:3, :3] = R_board_to_vehicle
        T_board_to_vehicle[:3, 3] = board_position
        
        print(f"\n棋盘格到车辆变换矩阵:")
        print(T_board_to_vehicle)
        
        # 使用PnP计算外参
        return self.from_pnp(objp, corners, camera_matrix, dist_coeffs, 
                            T_board_to_vehicle, use_fisheye)
    
    def transform_point_to_vehicle(self, point_camera: np.ndarray) -> np.ndarray:
        """
        将相机坐标系中的点转换到车辆坐标系
        
        Args:
            point_camera: 相机坐标系中的点 (x, y, z) 或 (N, 3)
            
        Returns:
            车辆坐标系中的点
        """
        if self.transformation_matrix is None:
            raise ValueError("外参未设置")
        
        point_camera = np.asarray(point_camera)
        if point_camera.ndim == 1:
            # 单个点
            point_homo = np.append(point_camera, 1)
            point_vehicle = self.transformation_matrix @ point_homo
            return point_vehicle[:3]
        else:
            # 多个点
            ones = np.ones((point_camera.shape[0], 1))
            points_homo = np.hstack([point_camera, ones])
            points_vehicle = (self.transformation_matrix @ points_homo.T).T
            return points_vehicle[:, :3]
    
    def get_calibration_result(self) -> dict:
        """
        获取标定结果
        
        Returns:
            包含外参的字典
        """
        if self.rotation_matrix is None or self.translation_vector is None:
            raise ValueError("外参未设置")
        
        # 计算欧拉角
        yaw, pitch, roll = mat2euler(self.rotation_matrix, 'szyx')
        
        return {
            'rotation_matrix': self.rotation_matrix.tolist(),
            'translation_vector': self.translation_vector.tolist(),
            'translation': self.translation_vector.tolist(),
            'transformation_matrix': self.transformation_matrix.tolist(),
            'euler_angles': {
                'roll': np.rad2deg(roll),
                'pitch': np.rad2deg(pitch),
                'yaw': np.rad2deg(yaw)
            },
            'rotation_euler': [np.rad2deg(roll), np.rad2deg(pitch), np.rad2deg(yaw)]
        }
    
    def load_from_dict(self, extrinsic_dict: dict):
        """
        从字典加载外参
        
        Args:
            extrinsic_dict: 包含外参的字典
        """
        self.rotation_matrix = np.array(extrinsic_dict['rotation_matrix'])
        self.translation_vector = np.array(extrinsic_dict['translation_vector'])
        self.transformation_matrix = np.array(extrinsic_dict['transformation_matrix'])
