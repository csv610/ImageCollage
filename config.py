from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from enum import Enum


class LayoutMode(Enum):
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"


@dataclass
class GridConfig:
    """Configuration for image grid collage generation"""
    input_path: Path
    canvas_width: int
    canvas_height: int
    layout: LayoutMode
    num_splits: int  # rows for horizontal, columns for vertical
    gap: int
    output_dir: Path
    max_size: Optional[int] = None
    background_color: str = "white"

    def __post_init__(self):
        """Validate configuration"""
        if self.canvas_width <= 0 or self.canvas_height <= 0:
            raise ValueError("Canvas width and height must be positive")
        if self.num_splits <= 0:
            raise ValueError("Number of splits must be positive")
        if self.gap < 0:
            raise ValueError("Gap cannot be negative")
        if self.max_size is not None and self.max_size <= 0:
            raise ValueError("Max size must be positive")
