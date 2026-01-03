from pathlib import Path
from PIL import Image
import numpy as np
from typing import List, Tuple


class ImageProcessor:
    """Handles image loading, resizing, and cropping"""

    @staticmethod
    def load_images(input_path: Path) -> List[Path]:
        """Load image paths from directory, sorted by filename"""
        if not input_path.is_dir():
            raise ValueError(f"{input_path} is not a directory")

        supported_formats = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
        image_paths = [
            p for p in sorted(input_path.iterdir())
            if p.suffix.lower() in supported_formats
        ]

        if not image_paths:
            raise ValueError(f"No images found in {input_path}")

        return image_paths

    @staticmethod
    def load_image(image_path: Path) -> Image.Image:
        """Load a single image"""
        img = Image.open(image_path)
        if img.mode == 'RGBA':
            # Convert RGBA to RGB
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[3])
            return background
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        return img

    @staticmethod
    def resize_and_crop(
        image: Image.Image,
        target_width: int,
        target_height: int,
        max_size: int = None
    ) -> Image.Image:
        """
        Resize and optionally crop image to fit target dimensions.

        Args:
            image: PIL Image object
            target_width: Target width
            target_height: Target height (can be None for aspect ratio calculation)
            max_size: Maximum size constraint (width for horizontal, height for vertical)

        Returns:
            Processed PIL Image
        """
        original_width, original_height = image.size
        aspect_ratio = original_width / original_height

        # If target_height is provided, resize to fit that height
        if target_height:
            new_height = target_height
            new_width = int(target_height * aspect_ratio)
        else:
            # Resize to fit target width, maintain aspect ratio
            new_width = target_width
            new_height = int(target_width / aspect_ratio)

        # Resize image
        resized = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # Apply max_size constraint if provided
        if max_size:
            if target_height:
                # Horizontal layout: max_size is max width
                if new_width > max_size:
                    # Crop from center
                    left = (new_width - max_size) // 2
                    resized = resized.crop((left, 0, left + max_size, new_height))
            else:
                # Vertical layout: max_size is max height
                if new_height > max_size:
                    # Crop from center
                    top = (new_height - max_size) // 2
                    resized = resized.crop((0, top, new_width, top + max_size))

        return resized

    @staticmethod
    def get_image_dimensions(image_path: Path) -> Tuple[int, int]:
        """Get image dimensions without loading full image"""
        img = Image.open(image_path)
        dimensions = img.size
        img.close()
        return dimensions
