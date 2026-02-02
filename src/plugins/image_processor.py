"""
Image Processor Plugin

Provides image preprocessing and enhancement capabilities.
"""

from pathlib import Path
from typing import Tuple, Optional
import logging

from PIL import Image, ImageEnhance, ImageFilter
from src.core.plugin_manager import Plugin
from src.core.plugin_config import (
    PluginConfigSchema,
    ConfigField,
    ConfigFieldType,
)


class ImageProcessor(Plugin):
    """Image preprocessing and enhancement plugin"""

    name = "image_processor"
    version = "1.0.0"
    dependencies = []

    # Define configuration schema
    config_schema = PluginConfigSchema()
    config_schema.add_field(ConfigField(
        name="default_format",
        field_type=ConfigFieldType.STRING,
        default="PNG",
        description="Default output format for images"
    ))
    config_schema.add_field(ConfigField(
        name="default_quality",
        field_type=ConfigFieldType.INTEGER,
        default=95,
        description="Default quality for JPEG images (1-100)",
        validator=lambda x: 1 <= x <= 100
    ))
    config_schema.add_field(ConfigField(
        name="max_size",
        field_type=ConfigFieldType.INTEGER,
        default=4096,
        description="Maximum image dimension (width or height)",
        validator=lambda x: x > 0
    ))

    def __init__(self) -> None:
        super().__init__()
        self._state["processed_count"] = 0

    def _get_config(self, key: str, default: any) -> any:
        """Helper to get config value safely"""
        if self.config:
            return self.config.get(key, default)
        return default

    def on_load(self) -> None:
        """Called when plugin is loaded"""
        super().on_load()
        self.logger.info("Image processor plugin loaded")

    def on_unload(self) -> None:
        """Called when plugin is unloaded"""
        super().on_unload()
        self.logger.info(
            f"Image processor plugin unloaded. "
            f"Processed {self._state['processed_count']} images"
        )

    def resize(
        self,
        input_path: str,
        output_path: str,
        size: Tuple[int, int],
        keep_aspect_ratio: bool = True
    ) -> str:
        """
        Resize an image

        Args:
            input_path: Path to input image
            output_path: Path to output image
            size: Target size (width, height)
            keep_aspect_ratio: Whether to maintain aspect ratio

        Returns:
            Path to resized image
        """
        try:
            img = Image.open(input_path)

            if keep_aspect_ratio:
                img.thumbnail(size, Image.Resampling.LANCZOS)
            else:
                img = img.resize(size, Image.Resampling.LANCZOS)

            # Get format from config or output path
            format_ext = Path(output_path).suffix.upper().lstrip(".")
            if not format_ext:
                format_ext = self._get_config("default_format", "PNG")

            img.save(output_path, format=format_ext)
            self._state["processed_count"] += 1

            self.logger.info(f"Resized image: {input_path} -> {output_path}")
            return output_path

        except Exception as e:
            self.logger.error(f"Failed to resize image: {e}")
            raise

    def crop(
        self,
        input_path: str,
        output_path: str,
        box: Tuple[int, int, int, int]
    ) -> str:
        """
        Crop an image

        Args:
            input_path: Path to input image
            output_path: Path to output image
            box: Crop box (left, top, right, bottom)

        Returns:
            Path to cropped image
        """
        try:
            img = Image.open(input_path)
            cropped = img.crop(box)

            # Get format from config or output path
            format_ext = Path(output_path).suffix.upper().lstrip(".")
            if not format_ext:
                format_ext = self._get_config("default_format", "PNG")

            cropped.save(output_path, format=format_ext)
            self._state["processed_count"] += 1

            self.logger.info(f"Cropped image: {input_path} -> {output_path}")
            return output_path

        except Exception as e:
            self.logger.error(f"Failed to crop image: {e}")
            raise

    def enhance(
        self,
        input_path: str,
        output_path: str,
        brightness: float = 1.0,
        contrast: float = 1.0,
        sharpness: float = 1.0,
        color: float = 1.0
    ) -> str:
        """
        Enhance an image

        Args:
            input_path: Path to input image
            output_path: Path to output image
            brightness: Brightness factor (1.0 = no change)
            contrast: Contrast factor (1.0 = no change)
            sharpness: Sharpness factor (1.0 = no change)
            color: Color saturation factor (1.0 = no change)

        Returns:
            Path to enhanced image
        """
        try:
            img = Image.open(input_path)

            # Apply enhancements
            if brightness != 1.0:
                enhancer = ImageEnhance.Brightness(img)
                img = enhancer.enhance(brightness)

            if contrast != 1.0:
                enhancer = ImageEnhance.Contrast(img)
                img = enhancer.enhance(contrast)

            if sharpness != 1.0:
                enhancer = ImageEnhance.Sharpness(img)
                img = enhancer.enhance(sharpness)

            if color != 1.0:
                enhancer = ImageEnhance.Color(img)
                img = enhancer.enhance(color)

            # Get format from config or output path
            format_ext = Path(output_path).suffix.upper().lstrip(".")
            if not format_ext:
                format_ext = self._get_config("default_format", "PNG")

            img.save(output_path, format=format_ext)
            self._state["processed_count"] += 1

            self.logger.info(f"Enhanced image: {input_path} -> {output_path}")
            return output_path

        except Exception as e:
            self.logger.error(f"Failed to enhance image: {e}")
            raise

    def convert_format(
        self,
        input_path: str,
        output_path: str,
        format: Optional[str] = None
    ) -> str:
        """
        Convert image format

        Args:
            input_path: Path to input image
            output_path: Path to output image
            format: Target format (e.g., "PNG", "JPEG")

        Returns:
            Path to converted image
        """
        try:
            img = Image.open(input_path)

            # Determine format
            if format:
                target_format = format.upper()
            else:
                format_ext = Path(output_path).suffix.upper().lstrip(".")
                target_format = format_ext if format_ext else self._get_config("default_format", "PNG")

            # Normalize format name (JPG -> JPEG)
            if target_format == "JPG":
                target_format = "JPEG"

            # Convert RGBA to RGB for JPEG
            if target_format == "JPEG" and img.mode == "RGBA":
                rgb_img = Image.new("RGB", img.size, (255, 255, 255))
                rgb_img.paste(img, mask=img.split()[3])
                img = rgb_img

            # Save with quality setting for JPEG
            if target_format == "JPEG":
                quality = self._get_config("default_quality", 95)
                img.save(output_path, format=target_format, quality=quality)
            else:
                img.save(output_path, format=target_format)

            self._state["processed_count"] += 1

            self.logger.info(f"Converted image: {input_path} -> {output_path}")
            return output_path

        except Exception as e:
            self.logger.error(f"Failed to convert image format: {e}")
            raise

    def apply_filter(
        self,
        input_path: str,
        output_path: str,
        filter_type: str = "BLUR"
    ) -> str:
        """
        Apply filter to image

        Args:
            input_path: Path to input image
            output_path: Path to output image
            filter_type: Filter type (BLUR, SHARPEN, SMOOTH, EDGE_ENHANCE)

        Returns:
            Path to filtered image
        """
        try:
            img = Image.open(input_path)

            # Apply filter
            filter_map = {
                "BLUR": ImageFilter.BLUR,
                "SHARPEN": ImageFilter.SHARPEN,
                "SMOOTH": ImageFilter.SMOOTH,
                "EDGE_ENHANCE": ImageFilter.EDGE_ENHANCE,
            }

            if filter_type not in filter_map:
                raise ValueError(f"Unknown filter type: {filter_type}")

            filtered = img.filter(filter_map[filter_type])

            # Get format from config or output path
            format_ext = Path(output_path).suffix.upper().lstrip(".")
            if not format_ext:
                format_ext = self._get_config("default_format", "PNG")

            filtered.save(output_path, format=format_ext)
            self._state["processed_count"] += 1

            self.logger.info(f"Applied {filter_type} filter: {input_path} -> {output_path}")
            return output_path

        except Exception as e:
            self.logger.error(f"Failed to apply filter: {e}")
            raise

    def get_stats(self) -> dict:
        """
        Get plugin statistics

        Returns:
            Dictionary with plugin statistics
        """
        return {
            "processed_count": self._state["processed_count"]
        }
