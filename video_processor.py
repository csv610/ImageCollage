from pathlib import Path
from PIL import Image
import cv2
from typing import List, Tuple


class VideoProcessor:
    """Handles video frame extraction"""

    @staticmethod
    def get_video_info(video_path: Path) -> Tuple[int, int, int, float]:
        """
        Get video information.

        Returns:
            (total_frames, width, height, fps)
        """
        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            raise ValueError(f"Cannot open video: {video_path}")

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)

        cap.release()
        return total_frames, width, height, fps

    @staticmethod
    def extract_frames(
        video_path: Path,
        num_frames: int,
        output_dir: Path = None
    ) -> List[Image.Image]:
        """
        Extract frames from video.

        Args:
            video_path: Path to video file
            num_frames: Number of frames to extract (evenly spaced)
            output_dir: Optional directory to save extracted frames

        Returns:
            List of PIL Image objects
        """
        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            raise ValueError(f"Cannot open video: {video_path}")

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        if num_frames > total_frames:
            raise ValueError(
                f"Requested {num_frames} frames but video has only {total_frames}"
            )

        # Calculate frame indices to extract (evenly spaced)
        frame_indices = [
            int(i * total_frames / num_frames)
            for i in range(num_frames)
        ]

        frames = []
        frame_count = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if frame_count in frame_indices:
                # Convert BGR to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(frame_rgb)
                frames.append(pil_image)

            frame_count += 1

        cap.release()

        if len(frames) != num_frames:
            raise ValueError(
                f"Expected {num_frames} frames but extracted {len(frames)}"
            )

        return frames

    @staticmethod
    def get_first_frame(video_path: Path) -> Image.Image:
        """Extract the first frame from video"""
        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            raise ValueError(f"Cannot open video: {video_path}")

        ret, frame = cap.read()
        cap.release()

        if not ret:
            raise ValueError(f"Cannot read first frame from {video_path}")

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return Image.fromarray(frame_rgb)
