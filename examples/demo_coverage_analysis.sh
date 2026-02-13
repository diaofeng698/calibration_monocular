#!/bin/bash
# 标定图像覆盖率分析 - 使用示例

echo "=============================================="
echo "标定图像覆盖率分析工具 - 示例演示"
echo "=============================================="
echo ""

# 设置目录
IMAGE_DIR="diao"
RESULTS_DIR="results"

# 创建结果目录
mkdir -p "$RESULTS_DIR"

echo "1. 基本分析（仅显示，不保存）"
echo "命令: python scripts/analyze_calibration_coverage.py --input $IMAGE_DIR"
echo ""
# python scripts/analyze_calibration_coverage.py --input "$IMAGE_DIR"

echo ""
echo "2. 分析并保存结果"
echo "命令: python scripts/analyze_calibration_coverage.py \\"
echo "         --input $IMAGE_DIR \\"
echo "         --output $RESULTS_DIR/coverage_analysis.png \\"
echo "         --report $RESULTS_DIR/coverage_report.txt"
echo ""
python scripts/analyze_calibration_coverage.py \
    --input "$IMAGE_DIR" \
    --output "$RESULTS_DIR/coverage_analysis.png" \
    --report "$RESULTS_DIR/coverage_report.txt"

echo ""
echo "=============================================="
echo "结果文件:"
echo "  可视化图像: $RESULTS_DIR/coverage_analysis.png"
echo "  详细报告:   $RESULTS_DIR/coverage_report.txt"
echo "=============================================="
echo ""

# 显示报告摘要
if [ -f "$RESULTS_DIR/coverage_report.txt" ]; then
    echo "报告摘要:"
    head -20 "$RESULTS_DIR/coverage_report.txt"
    echo ""
    echo "... (查看完整报告: cat $RESULTS_DIR/coverage_report.txt)"
fi

echo ""
echo "✅ 演示完成！"
echo ""
echo "下一步建议:"
echo "  1. 查看可视化图像，识别红色/空白区域"
echo "  2. 针对缺失区域补充标定图像"
echo "  3. 重新运行分析验证改进效果"
echo "  4. 使用完整图像集执行标定"
echo ""
