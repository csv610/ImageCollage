import argparse
import sys
from pathlib import Path
from PIL import Image
from typing import List, Tuple, Union

from config import GridConfig, LayoutMode
from image_processor import ImageProcessor
from video_processor import VideoProcessor
from layout import LayoutCalculator, ImagePlacement


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Create image collage grids from images or video frames"
    )

    parser.add_argument(
        "-i", "--input",
        type=Path,
        required=True,
        help="Input directory with images or video file"
    )

    parser.add_argument(
        "-c", "--canvas",
        type=int,
        nargs=2,
        default=[1920, 1080],
        metavar=("WIDTH", "HEIGHT"),
        help="Canvas width and height in pixels (default: 1920 1080)"
    )

    parser.add_argument(
        "-l", "--layout",
        choices=["horizontal", "vertical"],
        default="horizontal",
        help="Layout mode: horizontal (left-to-right rows) or vertical (top-to-bottom columns) (default: horizontal)"
    )

    parser.add_argument(
        "-n", "--splits",
        type=int,
        default=3,
        help="Number of splits (rows for horizontal, columns for vertical) (default: 3)"
    )

    parser.add_argument(
        "-g", "--gap",
        type=int,
        default=0,
        help="Gap between images in pixels (default: 0)"
    )

    parser.add_argument(
        "-s", "--max-size",
        type=int,
        default=None,
        help="Maximum size for images (optional)"
    )

    parser.add_argument(
        "-b", "--bg_color",
        type=int,
        nargs=3,
        default=[255, 255, 255],
        metavar=("R", "G", "B"),
        help="Canvas background color as RGB values 0-255 (default: 255 255 255)"
    )

    parser.add_argument(
        "-o", "--output",
        type=Path,
        default = "image_pages",
        help="Output directory for generated pages"
    )

    return parser.parse_args()


def load_images_or_video(input_path: Path, config: GridConfig) -> Tuple[Union[List[Path], List[Image.Image]], List[Tuple[int, int]]]:
    """
    Load images from directory or video file.

    Returns:
        For directories: (list of image paths, list of (width, height) tuples)
        For videos: (list of PIL Images, list of (width, height) tuples)
    """
    if input_path.is_dir():
        # Load image paths from directory (don't load images yet to avoid too many open files)
        image_paths = ImageProcessor.load_images(input_path)
        dimensions = []
        for img_path in image_paths:
            dim = ImageProcessor.get_image_dimensions(img_path)
            dimensions.append(dim)
        return image_paths, dimensions
    elif input_path.is_file():
        # Load from video
        total_frames, width, height, fps = VideoProcessor.get_video_info(input_path)
        print(f"Video contains {total_frames} frames")

        # Extract all frames from video
        frames = VideoProcessor.extract_frames(input_path, total_frames)
        dimensions = [(frame.size[0], frame.size[1]) for frame in frames]

        return frames, dimensions
    else:
        raise ValueError(f"{input_path} is neither a directory nor a file")


def process_images(
    config: GridConfig,
    images: List[Image.Image],
    dimensions: List[Tuple[int, int]]
) -> None:
    """
    Keep images in original dimensions. Processing will happen during page generation.
    """
    pass  # No pre-processing needed; will resize during placement


def generate_pages(
    config: GridConfig,
    images: Union[List[Path], List[Image.Image]],
    dimensions: List[Tuple[int, int]]
) -> None:
    """Generate and save collage pages"""
    config.output_dir.mkdir(parents=True, exist_ok=True)

    # Calculate layout
    pages, total_pages = LayoutCalculator.calculate_layout(config, dimensions)

    # Determine if images are paths (directory) or Image objects (video)
    is_image_path = isinstance(images[0], Path) if images else False

    # Track layout for output file
    layout_info = []

    # Generate each page
    for page_num, page_placements in enumerate(pages):
        # Create blank page with background color
        page = Image.new("RGB", (config.canvas_width, config.canvas_height), config.background_color)

        # Track images on this page
        page_images = []

        # Place images on page
        for placement in page_placements:
            img_idx = placement.image_idx

            if img_idx >= len(images):
                continue

            # Load image if it's a path, otherwise use the Image object
            if is_image_path:
                img = ImageProcessor.load_image(images[img_idx])
                image_name = images[img_idx].name
            else:
                img = images[img_idx]
                image_name = f"frame_{img_idx:03d}"

            page_images.append((img_idx, image_name))

            # Resize image to placement dimensions
            resized = img.resize((placement.width, placement.height), Image.Resampling.LANCZOS)

            # Paste onto page
            page.paste(resized, (placement.x, placement.y))

            # Close loaded image to free file handle
            if is_image_path:
                img.close()

        # Save page
        output_file = config.output_dir / f"page_{page_num:03d}.jpg"
        page.save(output_file, "JPEG", quality=95)
        print(f"Generated: {output_file}")

        # Record layout for this page
        layout_info.append((page_num, page_images))

    # Write layout information to file
    write_layout_file(config.output_dir, layout_info)


def write_layout_file(output_dir: Path, layout_info: List[Tuple[int, List[Tuple[int, str]]]]) -> None:
    """
    Write image layout information to image_layout.txt file.

    Args:
        output_dir: Directory to save the layout file
        layout_info: List of (page_num, page_images) tuples where page_images is list of (index, name) tuples
    """
    layout_file = output_dir / "image_layout.txt"

    with open(layout_file, "w") as f:
        for page_num, page_images in layout_info:
            f.write(f"page_{page_num:03d}.jpg: {', '.join(name for _, name in page_images)}\n")

    print(f"Layout information written to: {layout_file}")


def main():
    """Main entry point"""
    try:
        args = parse_arguments()

        # Create config
        config = GridConfig(
            input_path=args.input,
            canvas_width=args.canvas[0],
            canvas_height=args.canvas[1],
            layout=LayoutMode(args.layout),
            num_splits=args.splits,
            gap=args.gap,
            output_dir=args.output,
            max_size=args.max_size,
            background_color=tuple(args.bg_color)
        )

        print(f"Loading images from {config.input_path}...")
        images, dimensions = load_images_or_video(config.input_path, config)
        print(f"Loaded {len(images)} images")

        print("Generating pages...")
        generate_pages(config, images, dimensions)

        print("Done!")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
