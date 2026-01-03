from typing import List, Tuple
from dataclasses import dataclass
from config import LayoutMode, GridConfig


@dataclass
class ImagePlacement:
    """Information about how to place an image"""
    image_idx: int  # Index in original image list
    x: int
    y: int
    width: int
    height: int


class LayoutCalculator:
    """Calculates image positions and sizes for justified grid layout"""

    @staticmethod
    def calculate_layout_horizontal(
        config: GridConfig,
        image_dimensions: List[Tuple[int, int]]
    ) -> Tuple[List[List[ImagePlacement]], int]:
        """
        Calculate layout for horizontal layout (rows).

        Algorithm:
        - Fixed row height = (canvas_height - (num_rows-1)*gap) / num_rows
        - For each row, fit as many images as possible
        - Scale all images in row to same height, adjust width proportionally
        - Fill rows until page is full, then create new page
        """
        pages = []
        current_page_placements = []
        current_row_y = 0
        current_row_idx = 0
        image_idx = 0

        fixed_row_height = (
            config.canvas_height - (config.num_splits - 1) * config.gap
        ) // config.num_splits

        while image_idx < len(image_dimensions):
            # Check if we can add another row to current page
            if current_row_idx >= config.num_splits:
                # Page is full, start new page
                pages.append(current_page_placements)
                current_page_placements = []
                current_row_y = 0
                current_row_idx = 0

            # Collect images for this row
            row_images = []
            row_image_indices = []
            total_width = 0

            while image_idx < len(image_dimensions):
                img_w, img_h = image_dimensions[image_idx]
                aspect_ratio = img_w / img_h

                # Calculate width if image is scaled to fixed_row_height
                scaled_width = int(fixed_row_height * aspect_ratio)

                # Check if it fits in the row
                needed_width = scaled_width + (len(row_images) * config.gap)

                if total_width + needed_width > config.canvas_width and row_images:
                    # Doesn't fit, start placing this row
                    break

                row_images.append((img_w, img_h))
                row_image_indices.append(image_idx)
                total_width += scaled_width
                image_idx += 1

            # If no images fit, force at least one
            if not row_images:
                row_images.append(image_dimensions[image_idx])
                row_image_indices.append(image_idx)
                image_idx += 1

            # Place images in this row
            # Scale all images to fixed height, then adjust widths to fill canvas width
            row_placements = LayoutCalculator._place_row_horizontal(
                row_images,
                row_image_indices,
                config.canvas_width,
                fixed_row_height,
                config.gap,
                0,  # x position
                current_row_y,
                config.max_size
            )

            current_page_placements.extend(row_placements)
            current_row_y += fixed_row_height + config.gap
            current_row_idx += 1

        if current_page_placements:
            pages.append(current_page_placements)

        return pages, len(pages)

    @staticmethod
    def _place_row_horizontal(
        image_dims: List[Tuple[int, int]],
        indices: List[int],
        canvas_width: int,
        row_height: int,
        gap: int,
        x_offset: int,
        y_offset: int,
        max_size: int = None
    ) -> List[ImagePlacement]:
        """Place images in a horizontal row with justified alignment"""
        placements = []
        num_images = len(image_dims)

        # Calculate total width used by gaps
        total_gap_width = (num_images - 1) * gap if num_images > 1 else 0
        available_width = canvas_width - total_gap_width

        # Scale all images to row_height and calculate their widths
        image_widths = []
        for w, h in image_dims:
            aspect_ratio = w / h
            img_width = int(row_height * aspect_ratio)
            image_widths.append(img_width)

        total_natural_width = sum(image_widths)

        # Calculate scale factor to fill the canvas width
        scale_factor = available_width / total_natural_width if total_natural_width > 0 else 1

        # Place images
        current_x = x_offset
        for idx, (w, h) in enumerate(image_dims):
            final_width = int(image_widths[idx] * scale_factor)
            final_height = row_height

            # Apply max_size constraint if needed
            if max_size and final_width > max_size:
                final_width = max_size

            placement = ImagePlacement(
                image_idx=indices[idx],
                x=current_x,
                y=y_offset,
                width=final_width,
                height=final_height
            )
            placements.append(placement)
            current_x += final_width + gap

        return placements

    @staticmethod
    def calculate_layout_vertical(
        config: GridConfig,
        image_dimensions: List[Tuple[int, int]]
    ) -> Tuple[List[List[ImagePlacement]], int]:
        """
        Calculate layout for vertical layout (columns).

        Algorithm:
        - Fixed column width = (canvas_width - (num_cols-1)*gap) / num_cols
        - For each column, fit as many images as possible
        - Scale all images in column to same width, adjust height proportionally
        - Fill columns until page is full, then create new page
        """
        pages = []
        current_page_placements = []
        current_col_x = 0
        current_col_idx = 0
        image_idx = 0

        fixed_col_width = (
            config.canvas_width - (config.num_splits - 1) * config.gap
        ) // config.num_splits

        while image_idx < len(image_dimensions):
            # Check if we can add another column to current page
            if current_col_idx >= config.num_splits:
                # Page is full, start new page
                pages.append(current_page_placements)
                current_page_placements = []
                current_col_x = 0
                current_col_idx = 0

            # Collect images for this column
            col_images = []
            col_image_indices = []
            total_height = 0

            while image_idx < len(image_dimensions):
                img_w, img_h = image_dimensions[image_idx]
                aspect_ratio = img_w / img_h

                # Calculate height if image is scaled to fixed_col_width
                scaled_height = int(fixed_col_width / aspect_ratio)

                # Check if it fits in the column
                needed_height = scaled_height + (len(col_images) * config.gap)

                if total_height + needed_height > config.canvas_height and col_images:
                    # Doesn't fit, start placing this column
                    break

                col_images.append((img_w, img_h))
                col_image_indices.append(image_idx)
                total_height += scaled_height
                image_idx += 1

            # If no images fit, force at least one
            if not col_images:
                col_images.append(image_dimensions[image_idx])
                col_image_indices.append(image_idx)
                image_idx += 1

            # Place images in this column
            col_placements = LayoutCalculator._place_col_vertical(
                col_images,
                col_image_indices,
                fixed_col_width,
                config.canvas_height,
                config.gap,
                current_col_x,
                0,  # y position
                config.max_size
            )

            current_page_placements.extend(col_placements)
            current_col_x += fixed_col_width + config.gap
            current_col_idx += 1

        if current_page_placements:
            pages.append(current_page_placements)

        return pages, len(pages)

    @staticmethod
    def _place_col_vertical(
        image_dims: List[Tuple[int, int]],
        indices: List[int],
        col_width: int,
        canvas_height: int,
        gap: int,
        x_offset: int,
        y_offset: int,
        max_size: int = None
    ) -> List[ImagePlacement]:
        """Place images in a vertical column with justified alignment"""
        placements = []
        num_images = len(image_dims)

        # Calculate total height used by gaps
        total_gap_height = (num_images - 1) * gap if num_images > 1 else 0
        available_height = canvas_height - total_gap_height

        # Scale all images to col_width and calculate their heights
        image_heights = []
        for w, h in image_dims:
            aspect_ratio = w / h
            img_height = int(col_width / aspect_ratio)
            image_heights.append(img_height)

        total_natural_height = sum(image_heights)

        # Calculate scale factor to fill the canvas height
        scale_factor = available_height / total_natural_height if total_natural_height > 0 else 1

        # Place images
        current_y = y_offset
        for idx, (w, h) in enumerate(image_dims):
            final_width = col_width
            final_height = int(image_heights[idx] * scale_factor)

            # Apply max_size constraint if needed
            if max_size and final_height > max_size:
                final_height = max_size

            placement = ImagePlacement(
                image_idx=indices[idx],
                x=x_offset,
                y=current_y,
                width=final_width,
                height=final_height
            )
            placements.append(placement)
            current_y += final_height + gap

        return placements

    @staticmethod
    def calculate_layout(
        config: GridConfig,
        image_dimensions: List[Tuple[int, int]]
    ) -> Tuple[List[List[ImagePlacement]], int]:
        """
        Calculate layout for images based on layout mode.
        """
        if config.layout == LayoutMode.HORIZONTAL:
            return LayoutCalculator.calculate_layout_horizontal(config, image_dimensions)
        else:
            return LayoutCalculator.calculate_layout_vertical(config, image_dimensions)

    @staticmethod
    def calculate_required_images(
        config: GridConfig,
        first_image_dimensions: Tuple[int, int]
    ) -> int:
        """
        Calculate how many images are needed to fill the canvas pages.

        For video input, this helps determine how many frames to extract.
        """
        img_width, img_height = first_image_dimensions
        aspect_ratio = img_width / img_height

        if config.layout == LayoutMode.HORIZONTAL:
            fixed_height = (
                config.canvas_height - (config.num_splits - 1) * config.gap
            ) // config.num_splits
            images_per_row = max(1, config.canvas_width // (int(fixed_height * aspect_ratio) + config.gap))
            rows_per_page = config.num_splits
            images_per_page = images_per_row * rows_per_page
        else:  # VERTICAL
            fixed_width = (
                config.canvas_width - (config.num_splits - 1) * config.gap
            ) // config.num_splits
            img_height_in_col = int(fixed_width / aspect_ratio)
            images_per_col = max(1, config.canvas_height // (img_height_in_col + config.gap))
            cols_per_page = config.num_splits
            images_per_page = images_per_col * cols_per_page

        # For simplicity, estimate we need to fill 1-2 pages
        return max(images_per_page, 10)  # At least 10 images
