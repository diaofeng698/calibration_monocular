"""
Femto Bolt 相机接口类
支持RGB和深度图像采集
"""
import numpy as np
import cv2
try:
    import pyrealsense2 as rs
    REALSENSE_AVAILABLE = True
except ImportError:
    REALSENSE_AVAILABLE = False
    print("Warning: pyrealsense2 not installed. Using mock camera for testing.")


class FemtoBoltCamera:
    """Femto Bolt 深度相机接口"""
    
    def __init__(self, width=640, height=480, fps=30):
        """
        初始化相机
        
        Args:
            width: 图像宽度
            height: 图像高度
            fps: 帧率
        """
        self.width = width
        self.height = height
        self.fps = fps
        self.pipeline = None
        self.config = None
        
        if not REALSENSE_AVAILABLE:
            print("Running in mock mode. No actual camera will be used.")
            return
        
        try:
            self.pipeline = rs.pipeline()
            self.config = rs.config()
            
            # 配置RGB流
            self.config.enable_stream(rs.stream.color, width, height, rs.format.bgr8, fps)
            
            # 配置深度流
            self.config.enable_stream(rs.stream.depth, width, height, rs.format.z16, fps)
            
            print(f"Camera initialized: {width}x{height} @ {fps}fps")
        except Exception as e:
            print(f"Failed to initialize camera: {e}")
            self.pipeline = None
    
    def start(self):
        """启动相机"""
        if self.pipeline is None:
            print("Camera not available")
            return False
        
        try:
            self.pipeline.start(self.config)
            print("Camera started")
            return True
        except Exception as e:
            print(f"Failed to start camera: {e}")
            return False
    
    def stop(self):
        """停止相机"""
        if self.pipeline is not None:
            self.pipeline.stop()
            print("Camera stopped")
    
    def get_frames(self):
        """
        获取RGB和深度图像
        
        Returns:
            tuple: (color_image, depth_image) 或 (None, None) 如果失败
        """
        if self.pipeline is None:
            # 返回模拟图像用于测试
            color_image = np.zeros((self.height, self.width, 3), dtype=np.uint8)
            depth_image = np.zeros((self.height, self.width), dtype=np.uint16)
            return color_image, depth_image
        
        try:
            frames = self.pipeline.wait_for_frames()
            
            # 获取RGB帧
            color_frame = frames.get_color_frame()
            # 获取深度帧
            depth_frame = frames.get_depth_frame()
            
            if not color_frame or not depth_frame:
                return None, None
            
            # 转换为numpy数组
            color_image = np.asanyarray(color_frame.get_data())
            depth_image = np.asanyarray(depth_frame.get_data())
            
            return color_image, depth_image
        
        except Exception as e:
            print(f"Error getting frames: {e}")
            return None, None
    
    def get_intrinsics(self):
        """
        获取相机内参（从硬件读取）
        
        Returns:
            dict: 包含内参矩阵和畸变系数，如果不可用返回None
        """
        if self.pipeline is None:
            return None
        
        try:
            # 获取profile
            profile = self.pipeline.get_active_profile()
            color_profile = rs.video_stream_profile(profile.get_stream(rs.stream.color))
            intrinsics = color_profile.get_intrinsics()
            
            # 构建内参矩阵
            camera_matrix = np.array([
                [intrinsics.fx, 0, intrinsics.ppx],
                [0, intrinsics.fy, intrinsics.ppy],
                [0, 0, 1]
            ])
            
            # 畸变系数
            dist_coeffs = np.array(intrinsics.coeffs)
            
            return {
                'camera_matrix': camera_matrix,
                'distortion_coeffs': dist_coeffs,
                'width': intrinsics.width,
                'height': intrinsics.height
            }
        except Exception as e:
            print(f"Error getting intrinsics: {e}")
            return None
    
    def __enter__(self):
        """上下文管理器入口"""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.stop()
