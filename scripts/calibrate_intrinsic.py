#!/usr/bin/env python3
"""
相机内参标定
使用棋盘格图像进行标定
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import argparse
import cv2
from src.calibration import IntrinsicCalibration
from src.utils import save_calibration, visualize_calibration


def main():
    parser = argparse.ArgumentParser(description='相机内参标定')
    parser.add_argument('--input', type=str, required=True,
                       help='标定图像目录')
    parser.add_argument('--output', type=str, default='config/intrinsic.yaml',
                       help='输出文件路径')
    parser.add_argument('--checkerboard', type=int, nargs=2, default=[12, 8],
                       help='棋盘格内角点数量 (列 行)，默认: 12 8')
    parser.add_argument('--square-size', type=float, default=0.025,
                       help='棋盘格方格大小(米)，默认: 0.025')
    parser.add_argument('--show', action='store_true',
                       help='显示检测到的角点')
    args = parser.parse_args()
    
    print("\n" + "="*60)
    print("相机内参标定")
    print("="*60)
    print(f"\n标定参数:")
    print(f"  棋盘格大小: {args.checkerboard[0]} x {args.checkerboard[1]}")
    print(f"  方格尺寸: {args.square_size} 米")
    print(f"  图像目录: {args.input}")
    print("="*60 + "\n")
    
    # 创建标定器
    calibrator = IntrinsicCalibration(
        checkerboard_size=tuple(args.checkerboard),
        square_size=args.square_size
    )
    
    # 加载图像
    success_count = calibrator.load_images_from_folder(args.input)
    
    if success_count < 3:
        print("\n错误: 需要至少3张成功的标定图像")
        return
    
    # 读取一张图像获取尺寸
    image_files = [f for f in os.listdir(args.input) 
                   if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))]
    sample_image = cv2.imread(os.path.join(args.input, image_files[0]))
    image_size = (sample_image.shape[1], sample_image.shape[0])
    
    # 执行标定
    print("\n开始标定...")
    result = calibrator.calibrate(image_size)
    
    # 计算重投影误差
    mean_error = calibrator.calculate_reprojection_error()
    result['mean_reprojection_error'] = mean_error
    print(f"平均重投影误差: {mean_error:.4f} pixels")
    
    # 保存结果
    save_calibration(result, args.output)
    
    # 显示结果
    print("\n" + "="*60)
    # visualize_calibration(result)
    
    # # 测试去畸变
    # print("\n测试去畸变效果...")
    # test_image = sample_image.copy()
    # undistorted = calibrator.undistort_image(test_image)
    
    # # 显示对比
    # cv2.imshow('原始图像', test_image)
    # cv2.imshow('去畸变图像', undistorted)
    # print("按任意键关闭窗口...")
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    
    print("\n✓ 内参标定完成!")
    print(f"结果已保存到: {args.output}")


if __name__ == '__main__':
    main()
