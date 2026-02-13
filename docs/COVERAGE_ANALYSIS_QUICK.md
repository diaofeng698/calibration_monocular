# 标定图像覆盖率分析 - 快速参考

## 快速开始

```bash
# 基本分析
python scripts/analyze_calibration_coverage.py --input data/intrinsic_calibration

# 保存结果
python scripts/analyze_calibration_coverage.py \
    --input data/intrinsic_calibration \
    --output results/coverage.png \
    --report results/report.txt

# 自定义棋盘格 (9x6)
python scripts/analyze_calibration_coverage.py \
    --input data/intrinsic_calibration \
    --checkerboard 9 6 \
    --grid 10 8
```

## 参数速查

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--input` | 图像目录（必需） | - |
| `--checkerboard` | 棋盘格大小 (列 行) | 12 8 |
| `--grid` | 分析网格 (列 行) | 8 6 |
| `--output` | 保存图像路径 | 无 |
| `--report` | 保存报告路径 | 无 |

## 结果解读

### 颜色编码
- 🟩 **绿色** (>60%): 覆盖良好
- 🟨 **黄色** (30-60%): 覆盖一般  
- 🟥 **红色** (<30%): 需要补充

### 质量标准
- ✅ 20+ 张成功图像
- ✅ >70% 网格有覆盖
- ✅ 四角区域有覆盖
- ✅ 分布相对均匀

## 使用流程

1. **初次分析** → 识别缺失区域
2. **补充图像** → 针对红色/空白区域
3. **再次分析** → 验证改进效果
4. **执行标定** → 使用完整图像集

## 常见问题

**检测失败？** 检查图像质量和棋盘格参数  
**覆盖不均？** 增加边角和缺失区域的图像  
**网格太细？** 减小 `--grid` 参数  
**网格太粗？** 增大 `--grid` 参数

## 示例输出

```
找到 32 张图像
正在处理图像...
[1/32] ✓ image_001.png - 检测到 96 个角点
...
处理完成:
  成功: 32 张
  失败: 0 张

网格统计:
  • 空白网格: 8 个 (16.7%)
  • 低覆盖率: 12 个 (25.0%)
  • 高覆盖率: 13 个 (27.1%)
```

---
**详细文档**: [docs/COVERAGE_ANALYSIS.md](COVERAGE_ANALYSIS.md)
