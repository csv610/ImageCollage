# Image Collage

Creates image collage grids from a directory of images or video frames.

## Features

- Horizontal (row-based) or vertical (column-based) layout modes
- Pagination: creates multiple pages when content exceeds canvas size
- Supports video files; extracts frames to create collages
- Configurable gaps between images
- Optional max-size constraint for image cropping
- Generates `image_layout.txt` tracking which images appear on each page

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python main.py -i <input> -c <width> <height> [options]
```

### Required Arguments

- `-i, --input`: Input directory with images or video file path
- `-c, --canvas`: Canvas width and height in pixels (e.g., `-c 1920 1080`)

### Optional Arguments

- `-l, --layout`: Layout mode - `horizontal` (default) or `vertical`
  - `horizontal`: Fill left-to-right in rows, wrap to next row
  - `vertical`: Fill top-to-bottom in columns, wrap to next column
- `-n, --splits`: Number of splits (default: 3)
  - For horizontal: number of rows per page
  - For vertical: number of columns per page
- `-g, --gap`: Gap size between images in pixels (default: 0)
- `-s, --max-size`: Maximum image height/width for cropping (optional)
- `-b, --bg_color`: Canvas background color as RGB values (default: 255 255 255)
- `-o, --output`: Output directory (default: `image_pages`)

## Examples

Horizontal layout with 3 rows:
```bash
python main.py -i ./photos -c 1920 1080 -l horizontal -n 3 -g 10
```

Vertical layout with 2 columns:
```bash
python main.py -i ./photos -c 1920 1080 -l vertical -n 2 -g 5
```

From video file:
```bash
python main.py -i video.mp4 -c 1920 1080 -n 4
```

Specify output directory:
```bash
python main.py -i ./photos -c 1920 1080 -o ./output
```

## Output

Generated files in the output directory:
- Page images: `page_000.jpg`, `page_001.jpg`, etc.
- `image_layout.txt`: Lists which images appear on each page

Example `image_layout.txt`:
```
page_000.jpg: image1.jpg, image2.jpg, image3.jpg
page_001.jpg: image4.jpg, image5.jpg, image6.jpg
```

## Image Processing

- Images are sorted alphabetically by filename
- Images are resized to fit the layout while maintaining aspect ratio
- With `-s/--max-size`, images exceeding the size are cropped from center
- Supported formats: JPG, JPEG, PNG, GIF, BMP, WebP
