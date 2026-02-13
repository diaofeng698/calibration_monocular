#!/usr/bin/env python3
"""
Calibration Image Coverage Analysis Tool
Analyze the distribution of checkerboard corners in images and identify areas that need more images
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import argparse
import cv2
import numpy as np
import glob
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import matplotlib
matplotlib.use('TkAgg')  # Use TkAgg backend for Linux systems
matplotlib.rcParams['font.sans-serif'] = ['DejaVu Sans']  # Use default font
matplotlib.rcParams['axes.unicode_minus'] = False  # Fix minus sign display issue


class CalibrationCoverageAnalyzer:
    """Calibration image coverage analyzer"""
    
    def __init__(self, checkerboard_size=(12, 8), grid_size=(8, 6)):
        """
        Initialize the analyzer
        
        Args:
            checkerboard_size: Number of inner corners in checkerboard (cols, rows)
            grid_size: Grid size for analyzing distribution (cols, rows)
        """
        self.checkerboard_size = checkerboard_size
        self.grid_size = grid_size
        self.all_corners = []  # Store all detected corners
        self.image_size = None
        self.successful_images = []
        self.failed_images = []
        
    def find_corners(self, image: np.ndarray) -> np.ndarray:
        """
        Find checkerboard corners in image
        
        Args:
            image: Input image
            
        Returns:
            Corner coordinates array, or None if not found
        """
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Find checkerboard corners
        ret, corners = cv2.findChessboardCorners(
            gray, 
            self.checkerboard_size,
            cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_NORMALIZE_IMAGE
        )
        
        if ret:
            # Refine to sub-pixel accuracy
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
            corners = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
            return corners
        
        return None
    
    def analyze_folder(self, folder_path: str):
        """
        Analyze all calibration images in folder
        
        Args:
            folder_path: Path to calibration images folder
        """
        # Supported image formats
        image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.tiff', '*.JPG', '*.PNG']
        image_paths = []
        
        for ext in image_extensions:
            image_paths.extend(glob.glob(os.path.join(folder_path, ext)))
        
        if not image_paths:
            print(f"No image files found in {folder_path}")
            return
        
        print(f"\nFound {len(image_paths)} images")
        print("Processing images...")
        print("-" * 60)
        
        for i, img_path in enumerate(image_paths):
            img_name = os.path.basename(img_path)
            img = cv2.imread(img_path)
            
            if img is None:
                print(f"[{i+1}/{len(image_paths)}] ✗ {img_name} - Cannot read")
                self.failed_images.append(img_name)
                continue
            
            # Record image size
            if self.image_size is None:
                self.image_size = (img.shape[1], img.shape[0])  # (width, height)
            
            # Find corners
            corners = self.find_corners(img)
            
            if corners is not None:
                self.all_corners.append(corners.reshape(-1, 2))
                self.successful_images.append(img_name)
                print(f"[{i+1}/{len(image_paths)}] ✓ {img_name} - Detected {len(corners)} corners")
            else:
                self.failed_images.append(img_name)
                print(f"[{i+1}/{len(image_paths)}] ✗ {img_name} - No checkerboard detected")
        
        print("-" * 60)
        print(f"\nProcessing completed:")
        print(f"  Successful: {len(self.successful_images)} images")
        print(f"  Failed: {len(self.failed_images)} images")
        
        if self.failed_images:
            print(f"\nFailed images:")
            for img_name in self.failed_images:
                print(f"    - {img_name}")
    
    def compute_coverage_heatmap(self) -> np.ndarray:
        """
        Compute coverage heatmap
        
        Returns:
            Heatmap array (grid_rows, grid_cols)
        """
        if not self.all_corners or self.image_size is None:
            return None
        
        width, height = self.image_size
        grid_cols, grid_rows = self.grid_size
        
        # Create heatmap matrix
        heatmap = np.zeros((grid_rows, grid_cols), dtype=np.int32)
        
        # Calculate cell size
        cell_width = width / grid_cols
        cell_height = height / grid_rows
        
        # Count corners in each grid cell
        for corners in self.all_corners:
            for x, y in corners:
                # Calculate grid index for corner
                col_idx = int(x / cell_width)
                row_idx = int(y / cell_height)
                
                # Boundary check
                col_idx = min(col_idx, grid_cols - 1)
                row_idx = min(row_idx, grid_rows - 1)
                col_idx = max(col_idx, 0)
                row_idx = max(row_idx, 0)
                
                heatmap[row_idx, col_idx] += 1
        
        return heatmap
    
    def visualize_coverage(self, save_path: str = None):
        """
        Visualize coverage distribution
        
        Args:
            save_path: Path to save visualization, if None only display
        """
        if not self.all_corners or self.image_size is None:
            print("No data available for visualization")
            return
        
        # Create figure
        fig = plt.figure(figsize=(16, 10))
        
        # 1. Scatter plot of all corner points
        ax1 = plt.subplot(2, 2, 1)
        all_corners_array = np.vstack(self.all_corners)
        ax1.scatter(all_corners_array[:, 0], all_corners_array[:, 1], 
                   alpha=0.3, s=10, c='blue')
        ax1.set_xlim(0, self.image_size[0])
        ax1.set_ylim(self.image_size[1], 0)  # Invert y-axis
        ax1.set_aspect('equal')
        ax1.set_title(f'All Corner Points Distribution (Total: {len(all_corners_array)} points)', 
                     fontsize=14, fontweight='bold')
        ax1.set_xlabel('X (pixels)')
        ax1.set_ylabel('Y (pixels)')
        ax1.grid(True, alpha=0.3)
        
        # 2. Coverage heatmap
        ax2 = plt.subplot(2, 2, 2)
        heatmap = self.compute_coverage_heatmap()
        
        im = ax2.imshow(heatmap, cmap='hot', interpolation='nearest', aspect='auto')
        ax2.set_title('Coverage Heatmap (Grid Statistics)', 
                     fontsize=14, fontweight='bold')
        ax2.set_xlabel('Grid Column')
        ax2.set_ylabel('Grid Row')
        
        # Add colorbar
        cbar = plt.colorbar(im, ax=ax2)
        cbar.set_label('Corner Count')
        
        # Annotate each grid cell with count
        heatmap_rows, heatmap_cols = heatmap.shape
        for i in range(heatmap_rows):
            for j in range(heatmap_cols):
                text_color = 'white' if heatmap[i, j] > heatmap.max() / 2 else 'black'
                ax2.text(j, i, str(heatmap[i, j]), 
                        ha="center", va="center", 
                        color=text_color, fontsize=10, fontweight='bold')
        
        # 3. Coverage distribution overlay
        ax3 = plt.subplot(2, 2, 3)
        
        # Create background image
        width, height = self.image_size
        background = np.ones((height, width, 3), dtype=np.uint8) * 240
        
        # Draw grid
        grid_cols, grid_rows = self.grid_size
        cell_width = width / grid_cols
        cell_height = height / grid_rows
        
        # Color each grid cell based on coverage
        coverage_img = background.copy()
        max_count = heatmap.max()
        
        for i in range(grid_rows):
            for j in range(grid_cols):
                x1 = int(j * cell_width)
                y1 = int(i * cell_height)
                x2 = int((j + 1) * cell_width)
                y2 = int((i + 1) * cell_height)
                
                # Calculate color based on coverage ratio (red to green)
                ratio = heatmap[i, j] / max_count if max_count > 0 else 0
                
                # Red (low coverage) to green (high coverage)
                if ratio < 0.3:
                    color = (255, 100, 100)  # Red - needs more images
                elif ratio < 0.6:
                    color = (255, 255, 100)  # Yellow - medium coverage
                else:
                    color = (100, 255, 100)  # Green - good coverage
                
                cv2.rectangle(coverage_img, (x1, y1), (x2, y2), color, -1)
                cv2.rectangle(coverage_img, (x1, y1), (x2, y2), (100, 100, 100), 2)
        
        # Overlay corner points
        for corners in self.all_corners:
            for x, y in corners:
                cv2.circle(coverage_img, (int(x), int(y)), 3, (0, 0, 255), -1)
        
        ax3.imshow(cv2.cvtColor(coverage_img, cv2.COLOR_BGR2RGB))
        ax3.set_title('Coverage Distribution (Red=Need More, Yellow=Medium, Green=Good)', 
                     fontsize=11, fontweight='bold')
        ax3.axis('off')
        
        # 4. Statistics
        ax4 = plt.subplot(2, 2, 4)
        ax4.axis('off')
        
        # Calculate statistics
        total_cells = grid_rows * grid_cols
        empty_cells = np.sum(heatmap == 0)
        low_coverage_cells = np.sum((heatmap > 0) & (heatmap < heatmap.max() * 0.3))
        medium_coverage_cells = np.sum((heatmap >= heatmap.max() * 0.3) & 
                                       (heatmap < heatmap.max() * 0.6))
        high_coverage_cells = np.sum(heatmap >= heatmap.max() * 0.6)
        
        avg_corners_per_cell = heatmap.mean()
        std_corners_per_cell = heatmap.std()
        
        # Find regions that need more images
        need_supplement_regions = []
        for i in range(grid_rows):
            for j in range(grid_cols):
                if heatmap[i, j] < heatmap.max() * 0.3:
                    need_supplement_regions.append((i, j, heatmap[i, j]))
        
        # Display statistics
        stats_text = f"""
Calibration Image Coverage Report
{'='*50}

Image Information:
  • Image size: {self.image_size[0]} x {self.image_size[1]} pixels
  • Successful: {len(self.successful_images)} images
  • Failed: {len(self.failed_images)} images
  • Total corners: {len(all_corners_array)}

Grid Statistics ({grid_cols} x {grid_rows} = {total_cells} cells):
  • Empty cells: {empty_cells} ({empty_cells/total_cells*100:.1f}%)
  • Low coverage: {low_coverage_cells} ({low_coverage_cells/total_cells*100:.1f}%)
  • Medium coverage: {medium_coverage_cells} ({medium_coverage_cells/total_cells*100:.1f}%)
  • High coverage: {high_coverage_cells} ({high_coverage_cells/total_cells*100:.1f}%)

Corner Distribution:
  • Average per cell: {avg_corners_per_cell:.1f} corners
  • Std deviation: {std_corners_per_cell:.1f}
  • Maximum: {heatmap.max()} corners
  • Minimum: {heatmap.min()} corners

Regions needing more images (row, col, current corners):
"""
        
        if need_supplement_regions:
            # Sort by corner count, lowest first
            need_supplement_regions.sort(key=lambda x: x[2])
            for i, (row, col, count) in enumerate(need_supplement_regions[:10]):  # Show top 10
                stats_text += f"  {i+1}. Cell[{row}, {col}]: {count} corners\n"
            if len(need_supplement_regions) > 10:
                stats_text += f"  ... and {len(need_supplement_regions) - 10} more regions\n"
        else:
            stats_text += "  ✓ All regions well covered!\n"
        
        stats_text += f"\n{'='*50}\n"
        stats_text += "Recommendations:\n"
        if empty_cells > 0:
            stats_text += f"  • {empty_cells} empty cells, add images for these areas\n"
        if low_coverage_cells > total_cells * 0.3:
            stats_text += f"  • Many low coverage areas, add more images from different angles\n"
        if std_corners_per_cell > avg_corners_per_cell * 0.5:
            stats_text += f"  • Uneven corner distribution, add images for low coverage areas\n"
        if len(self.successful_images) < 20:
            stats_text += f"  • Too few images, recommend at least 20 successful images\n"
        
        ax4.text(0.05, 0.95, stats_text, 
                transform=ax4.transAxes,
                fontsize=10,
                verticalalignment='top',
                fontfamily='monospace',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))
        
        plt.tight_layout()
        
        # Save or display
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"\nVisualization saved to: {save_path}")
        
        plt.show()
    
    def generate_coverage_report(self, output_file: str = None):
        """
        Generate detailed text report
        
        Args:
            output_file: Output file path, if None print to console
        """
        if not self.all_corners or self.image_size is None:
            print("No data available to generate report")
            return
        
        heatmap = self.compute_coverage_heatmap()
        grid_rows, grid_cols = self.grid_size
        
        report = []
        report.append("\n" + "="*70)
        report.append("Calibration Image Coverage Detailed Report")
        report.append("="*70)
        report.append(f"\nGenerated: {np.datetime64('now')}")
        report.append(f"Image size: {self.image_size[0]} x {self.image_size[1]} pixels")
        report.append(f"Grid division: {grid_cols} x {grid_rows}")
        report.append(f"Successful: {len(self.successful_images)} images")
        report.append(f"Failed: {len(self.failed_images)} images")
        
        # Grid details
        report.append("\n" + "-"*70)
        report.append("Grid Coverage Details:")
        report.append("-"*70)
        report.append(f"{'Cell[row,col]':<15} {'Corners':<10} {'Coverage':<10} {'Status'}")
        report.append("-"*70)
        
        heatmap_rows, heatmap_cols = heatmap.shape
        max_count = heatmap.max()
        for i in range(heatmap_rows):
            for j in range(heatmap_cols):
                count = heatmap[i, j]
                ratio = count / max_count if max_count > 0 else 0
                
                if count == 0:
                    status = "⚠ Empty"
                elif ratio < 0.3:
                    status = "⚠ Need more"
                elif ratio < 0.6:
                    status = "○ Medium"
                else:
                    status = "✓ Good"
                
                report.append(f"Cell[{i:2d},{j:2d}]      {count:4d}       "
                            f"{ratio*100:5.1f}%     {status}")
        
        report.append("\n" + "="*70)
        
        report_text = "\n".join(report)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_text)
            print(f"Detailed report saved to: {output_file}")
        else:
            print(report_text)


def main():
    parser = argparse.ArgumentParser(
        description='Analyze coverage distribution of checkerboard corners in calibration images',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage
  python scripts/analyze_calibration_coverage.py --input data/intrinsic_calibration
  
  # Custom checkerboard and grid size
  python scripts/analyze_calibration_coverage.py --input data/intrinsic_calibration \\
      --checkerboard 12 8 --grid 10 8
  
  # Save results
  python scripts/analyze_calibration_coverage.py --input data/intrinsic_calibration \\
      --output results/coverage_analysis.png --report results/coverage_report.txt
        """
    )
    
    parser.add_argument('--input', type=str, required=True,
                       help='Calibration images directory')
    parser.add_argument('--checkerboard', type=int, nargs=2, default=[12, 8],
                       help='Checkerboard inner corners (cols rows), default: 12 8')
    parser.add_argument('--grid', type=int, nargs=2, default=[8, 6],
                       help='Analysis grid size (cols rows), default: 8 6')
    parser.add_argument('--output', type=str, default=None,
                       help='Visualization output path (PNG format)')
    parser.add_argument('--report', type=str, default=None,
                       help='Detailed report output path (TXT format)')
    
    args = parser.parse_args()
    
    print("\n" + "="*70)
    print("Calibration Image Coverage Analysis Tool")
    print("="*70)
    print(f"\nAnalysis Parameters:")
    print(f"  Checkerboard size: {args.checkerboard[0]} x {args.checkerboard[1]}")
    print(f"  Analysis grid: {args.grid[0]} x {args.grid[1]}")
    print(f"  Image directory: {args.input}")
    if args.output:
        print(f"  Output image: {args.output}")
    if args.report:
        print(f"  Output report: {args.report}")
    print("="*70)
    
    # 创建分析器
    analyzer = CalibrationCoverageAnalyzer(
        checkerboard_size=tuple(args.checkerboard),
        grid_size=tuple(args.grid)
    )
    
    # Analyze images
    analyzer.analyze_folder(args.input)
    
    if len(analyzer.all_corners) == 0:
        print("\nError: No checkerboard detected, please check:")
        print("  1. Image file format is correct")
        print("  2. Checkerboard parameters are correct")
        print("  3. Image quality is sufficient")
        return
    
    # Visualize results
    analyzer.visualize_coverage(save_path=args.output)
    
    # Generate detailed report
    if args.report:
        analyzer.generate_coverage_report(output_file=args.report)


if __name__ == '__main__':
    main()
