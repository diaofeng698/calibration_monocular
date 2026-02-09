#!/usr/bin/env python3
"""
采集标定图像
用于内参标定的图像采集脚本
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import cv2
import argparse
from datetime import datetime
from src.camera import FemtoBoltCamera


def main():
    parser = argparse.ArgumentParser(description='采集相机标定图像')
    parser.add_argument('--output', type=str, default='data/intrinsic_calibration',
                       help='输出目录')
    parser.add_argument('--width', type=int, default=640,
                       help='图像宽度')
    parser.add_argument('--height', type=int, default=480,
                       help='图像高度')
    parser.add_argument('--fps', type=int, default=30,
                       help='帧率')
    args = parser.parse_args()
    
    # 创建输出目录
    os.makedirs(args.output, exist_ok=True)
    
    # 初始化相机
    camera = FemtoBoltCamera(width=args.width, height=args.height, fps=args.fps)
    
    if not camera.start():
        print("无法启动相机，使用模拟模式进行演示")
    
    print("\n" + "="*60)
    print("标定图像采集")
    print("="*60)
    print("\n使用说明:")
    print("  - 将棋盘格标定板放置在不同位置和角度")
    print("  - 按 SPACE 键保存当前图像")
    print("  - 按 'q' 键退出")
    print("\n建议:")
    print("  - 采集20-30张图像")
    print("  - 覆盖图像的不同区域")
    print("  - 包含不同距离和角度")
    print("  - 保持标定板完全可见且清晰")
    print("="*60 + "\n")
    
    image_count = 0
    
    try:
        while True:
            # 获取图像
            color_image, depth_image = camera.get_frames()
            
            if color_image is None:
                print("无法获取图像")
                break
            
            # 显示图像
            display_image = color_image.copy()
            cv2.putText(display_image, f"已保存: {image_count} 张", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(display_image, "SPACE=保存 | Q=退出", 
                       (10, display_image.shape[0] - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            cv2.imshow('采集标定图像', display_image)
            
            key = cv2.waitKey(1) & 0xFF
            
            # 按空格键保存图像
            if key == ord(' '):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = os.path.join(args.output, f"calib_{image_count:03d}_{timestamp}.png")
                cv2.imwrite(filename, color_image)
                print(f"✓ 已保存: {filename}")
                image_count += 1
            
            # 按q键退出
            elif key == ord('q'):
                break
    
    except KeyboardInterrupt:
        print("\n用户中断")
    
    finally:
        camera.stop()
        cv2.destroyAllWindows()
    
    print(f"\n共采集 {image_count} 张图像")
    print(f"图像保存在: {args.output}")
    
    if image_count >= 10:
        print("\n✓ 图像数量充足，可以进行标定")
    else:
        print("\n⚠ 建议采集至少10张图像以获得更好的标定效果")


if __name__ == '__main__':
    main()
