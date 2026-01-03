# Image Collage - Requirements Specification

## Input
- `-i`: Image directory or video file path

## Canvas Configuration
- `-w` or `--width`: Canvas page width (in pixels) - **REQUIRED**
- `--height`: Canvas page height (in pixels) - **REQUIRED**
- `-l` or `--layout`: Layout mode - `horizontal` or `vertical` (default: horizontal)
  - `horizontal`: Fill left-to-right in rows, wrap to next row
  - `vertical`: Fill top-to-bottom in columns, wrap to next column
- `-n` or `--splits`: Number of splits (default: 3)
  - For horizontal: number of rows per page
  - For vertical: number of columns per page

## Image Processing
- `-s` or `--max-size`: Maximum image height (optional)
  - If set and image height exceeds it, crop from center
  - If not set, maintain aspect ratio
- Images sorted by filename (alphabetically)
- Every image resized to fit the region width completely

## Spacing
- `-g` or `--gap`: Gap size between images (both horizontal and vertical)
- Gaps reduce available width/height for images

## Output
- `-o` or `--output`: Output directory for generated page images
  - Short form: `-o`
  - Long form: `--output`
- Each page is a separate image file (e.g., page_0.jpg, page_1.jpg, etc.)
- Canvas pages are created as needed when content exceeds page dimensions

## Video Processing
1. Extract first frame to determine dimensions
2. Use first frame dimensions to estimate how many images fit per page
3. Calculate total images needed to fill required pages
4. Extract exactly that many frames from video

## Layout Algorithm
- Images arranged in reading order based on layout mode
- Gaps reduce available space for images
- When content exceeds page dimensions, create new page
- Paginated output with separate image files
