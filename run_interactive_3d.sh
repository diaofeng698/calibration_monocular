#!/bin/bash
# 实时3D可视化 - 命令速查表
# 快速运行各种3D可视化命令

echo ""
echo "=========================================="
echo "  实时3D可视化 - 命令速查表"
echo "=========================================="
echo ""

# 显示菜单
cat << 'MENU'
可用命令:

【基础测试】
1. 快速环境测试
   python test_interactive_3d.py

【单相机显示】
2. 前置中央相机
   python scripts/view_3d_interactive.py --position 1.5 0.0 1.8 --orientation 0.0 -10.0 0.0

3. 前置左侧相机
   python scripts/view_3d_interactive.py --position 1.8 0.8 1.5 --orientation 0.0 -15.0 10.0

4. 前置右侧相机
   python scripts/view_3d_interactive.py --position 1.8 -0.8 1.5 --orientation 0.0 -15.0 -10.0

5. 后置相机
   python scripts/view_3d_interactive.py --position -0.5 0.0 2.0 --orientation 0.0 -20.0 180.0

【多相机显示】
6. 测试4个相机位置
   python examples/test_interactive_3d.py

【高级功能】
7. 自动旋转动画
   python scripts/view_3d_interactive.py --position 1.5 0.0 1.8 --orientation 0.0 -10.0 0.0 --animate

8. SUV大车型
   python scripts/view_3d_interactive.py --position 2.5 0.0 1.9 --orientation 0.0 -12.0 0.0 --car-length 5.0 --car-width 2.2

9. 隐藏相机坐标系
   python scripts/view_3d_interactive.py --position 1.5 0.0 1.8 --orientation 0.0 -10.0 0.0 --hide-camera-frame

【示例集】
10. 完整示例集（6个示例）
    python examples/realtime_3d_examples.py

【使用外参文件】
11. 从配置文件加载
    python scripts/view_3d_interactive.py --extrinsic config/extrinsic.yaml

【帮助】
12. 查看所有参数
    python scripts/view_3d_interactive.py --help

MENU

echo ""
echo "=========================================="
echo "  交互操作提示"
echo "=========================================="
echo ""
echo "在3D窗口中:"
echo "  • 鼠标左键拖动: 旋转"
echo "  • 鼠标右键拖动: 平移"
echo "  • 鼠标滚轮: 缩放"
echo "  • 按 'r' 键: 重置视角"
echo "  • 按 's' 键: 保存截图"
echo "  • 按 'q' 键: 退出"
echo ""

# 询问是否执行命令
read -p "请选择命令编号 (1-12) 或按 Enter 退出: " choice

case $choice in
    1)
        echo "执行: 快速环境测试"
        python test_interactive_3d.py
        ;;
    2)
        echo "执行: 前置中央相机"
        python scripts/view_3d_interactive.py --position 1.5 0.0 1.8 --orientation 0.0 -10.0 0.0
        ;;
    3)
        echo "执行: 前置左侧相机"
        python scripts/view_3d_interactive.py --position 1.8 0.8 1.5 --orientation 0.0 -15.0 10.0
        ;;
    4)
        echo "执行: 前置右侧相机"
        python scripts/view_3d_interactive.py --position 1.8 -0.8 1.5 --orientation 0.0 -15.0 -10.0
        ;;
    5)
        echo "执行: 后置相机"
        python scripts/view_3d_interactive.py --position -0.5 0.0 2.0 --orientation 0.0 -20.0 180.0
        ;;
    6)
        echo "执行: 测试4个相机位置"
        python examples/test_interactive_3d.py
        ;;
    7)
        echo "执行: 自动旋转动画"
        python scripts/view_3d_interactive.py --position 1.5 0.0 1.8 --orientation 0.0 -10.0 0.0 --animate
        ;;
    8)
        echo "执行: SUV大车型"
        python scripts/view_3d_interactive.py --position 2.5 0.0 1.9 --orientation 0.0 -12.0 0.0 --car-length 5.0 --car-width 2.2
        ;;
    9)
        echo "执行: 隐藏相机坐标系"
        python scripts/view_3d_interactive.py --position 1.5 0.0 1.8 --orientation 0.0 -10.0 0.0 --hide-camera-frame
        ;;
    10)
        echo "执行: 完整示例集"
        python examples/realtime_3d_examples.py
        ;;
    11)
        echo "执行: 从配置文件加载"
        if [ -f "config/extrinsic.yaml" ]; then
            python scripts/view_3d_interactive.py --extrinsic config/extrinsic.yaml
        else
            echo "错误: config/extrinsic.yaml 文件不存在"
            echo "请先运行标定程序生成外参文件，或使用其他命令"
        fi
        ;;
    12)
        echo "执行: 查看所有参数"
        python scripts/view_3d_interactive.py --help
        ;;
    "")
        echo "退出"
        ;;
    *)
        echo "无效的选择: $choice"
        ;;
esac

echo ""
echo "=========================================="
echo "  更多信息"
echo "=========================================="
echo ""
echo "文档:"
echo "  • 快速参考: QUICK_REFERENCE.md"
echo "  • 详细指南: INTERACTIVE_3D_GUIDE.md"
echo "  • 实现说明: REALTIME_3D_IMPLEMENTATION.md"
echo "  • 更新日志: CHANGELOG_REALTIME_3D.md"
echo ""
