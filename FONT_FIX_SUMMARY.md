# 3D可视化字体问题修复总结

## ✅ 问题已解决

### 修复内容
已将3D可视化图像中的所有中文标签改为英文，避免字体显示问题。

### 修改的文件

#### 1. src/utils/visualization.py
- `plot_camera_pose_3d()` 函数中的所有标签改为英文
- 图例标签：
  - "X (前)" → "X (Forward)"
  - "Y (左)" → "Y (Left)"
  - "Z (上)" → "Z (Up)"
  - "相机" → "Camera"
  - "车辆轮廓" → "Vehicle Outline"
- 坐标轴标签：
  - "X (前) [m]" → "X (Forward) [m]"
  - "Y (左) [m]" → "Y (Left) [m]"
  - "Z (上) [m]" → "Z (Up) [m]"
- 图像标题：
  - "相机在车辆坐标系中的位置" → "Camera Position in Vehicle Coordinate System"

#### 2. scripts/calibrate_extrinsic_manual.py
- 添加了异常处理，无GUI环境下优雅降级
- 保持控制台输出为中文（便于理解）

#### 3. scripts/calibrate_extrinsic_auto.py
- 添加了异常处理，确保与手动脚本一致

### 测试结果

✅ **完全消除字体警告**
```bash
# 之前：大量 "Glyph missing from font" 警告
# 现在：无任何字体警告
```

✅ **3D图像正常生成**
- 文件：config/camera_pose_3d.png
- 格式：PNG (1500x1200, RGBA)
- 大小：270KB
- 质量：150 DPI

✅ **所有功能正常**
```bash
$ python test_installation.py
🎉 所有测试通过！
```

### 使用示例

```bash
# 手动外参标定（无警告）
python scripts/calibrate_extrinsic_manual.py \
    --position 1.5 0.0 1.8 \
    --orientation 0.0 -10.0 0.0 \
    --output config/extrinsic.yaml

# 输出清晰，无字体警告
# 自动生成：config/camera_pose_3d.png
```

### 设计原则

1. **图像使用英文**
   - 3D可视化图像标签使用英文
   - 避免字体兼容性问题
   - 国际化友好

2. **控制台保持中文**
   - 终端输出保持中文
   - 便于中文用户理解
   - 更好的用户体验

3. **文档保持中文**
   - README、USAGE等文档保持中文
   - 便于学习和维护
   - 适合中文用户群体

### 优点

✓ 跨平台兼容性好
✓ 无需安装中文字体
✓ 图像更专业、清晰
✓ 避免乱码问题
✓ 国际化友好

### 相关文件

- `src/utils/visualization.py` - 主要修改
- `scripts/calibrate_extrinsic_manual.py` - 异常处理
- `scripts/calibrate_extrinsic_auto.py` - 异常处理
- `config/camera_pose_3d.png` - 生成的图像
- `CHANGELOG.md` - 详细更新日志

### 后续建议

如需进一步优化，可以考虑：
1. 添加字体配置选项（可选中文/英文）
2. 支持自定义字体路径
3. 提供更多可视化样式选项

---
**修复时间**: 2026-01-27  
**状态**: ✅ 已完成并测试通过
