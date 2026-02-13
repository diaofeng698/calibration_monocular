# Coverage Analysis Tool - Changelog

## Version 1.1 - 2026-02-13

### 🌍 Full English Translation
- **Complete language conversion**: All Chinese text replaced with English
- **Eliminated font warnings**: No more missing glyph warnings on Linux systems
- **Better cross-platform compatibility**: Works seamlessly on all systems without font configuration

### Changes in Detail

#### User-Facing Text
- ✅ Help messages and command descriptions
- ✅ Console output and progress messages
- ✅ Statistics report and visualization labels
- ✅ Error messages and warnings
- ✅ Status indicators (Empty, Need more, Medium, Good)

#### Code Documentation
- ✅ Docstrings and function descriptions
- ✅ Class and method documentation
- ✅ Inline comments
- ✅ Example usage in help text

#### Output Files
- ✅ Visualization titles and labels
- ✅ Text report headers and sections
- ✅ Statistical information display
- ✅ Recommendations text

### Benefits

1. **No Font Issues**: Eliminated all Chinese character font warnings
2. **Universal Compatibility**: Works on any system without special font configuration
3. **Professional Appearance**: Clean English output suitable for international use
4. **Better Performance**: No font fallback delays or warnings

### Migration Notes

- All functionality remains the same
- Command-line interface unchanged
- Output file formats unchanged
- Only display language changed from Chinese to English

### Test Results

```bash
# Successfully tested on:
- Ubuntu Linux
- 34 calibration images
- All features working correctly
- No font warnings
```

---

## Version 1.0 - 2026-02-13

### 🎉 Initial Release

#### Core Features
- Checkerboard corner detection and analysis
- Coverage heatmap generation
- Color-coded distribution visualization
- Detailed statistical reports
- Flexible parameter configuration

#### Supported Operations
- Analyze calibration image folders
- Generate coverage heatmaps
- Identify areas needing more images
- Export visualization and reports
- Custom checkerboard and grid sizes

#### Output Formats
- PNG visualization (4-panel layout)
- TXT detailed report
- Console progress output

---

**Note**: For detailed usage instructions, see [docs/COVERAGE_ANALYSIS.md](docs/COVERAGE_ANALYSIS.md)
