"""Tests for image processor plugin"""

import pytest
from pathlib import Path
from PIL import Image
from src.plugins.image_processor import ImageProcessor


@pytest.fixture
def test_image(tmp_path):
    """Create a test image"""
    img_path = tmp_path / "test.png"
    img = Image.new("RGB", (100, 100), color="red")
    img.save(img_path)
    return str(img_path)


@pytest.fixture
def test_image_rgba(tmp_path):
    """Create a test RGBA image"""
    img_path = tmp_path / "test_rgba.png"
    img = Image.new("RGBA", (100, 100), color=(255, 0, 0, 128))
    img.save(img_path)
    return str(img_path)


@pytest.fixture
def plugin(tmp_path):
    """Create image processor plugin instance"""
    return ImageProcessor()


class TestImageProcessor:
    """Test ImageProcessor plugin"""

    def test_plugin_initialization(self, plugin):
        """Test plugin initialization"""
        assert plugin.name == "image_processor"
        assert plugin.version == "1.0.0"
        assert plugin.dependencies == []
        assert plugin._state["processed_count"] == 0

    def test_plugin_lifecycle(self, plugin):
        """Test plugin lifecycle hooks"""
        plugin.on_load()
        assert plugin._state["processed_count"] == 0

        plugin._state["processed_count"] = 5
        plugin.on_unload()
        # State should still be preserved
        assert plugin._state["processed_count"] == 5

    def test_resize_with_aspect_ratio(self, plugin, test_image, tmp_path):
        """Test resizing image with aspect ratio"""
        output_path = tmp_path / "resized.png"

        result = plugin.resize(
            test_image,
            str(output_path),
            (50, 50),
            keep_aspect_ratio=True
        )

        assert result == str(output_path)
        assert output_path.exists()

        # Check image was resized
        img = Image.open(output_path)
        assert img.size[0] <= 50
        assert img.size[1] <= 50

        # Check processed count
        assert plugin._state["processed_count"] == 1

    def test_resize_without_aspect_ratio(self, plugin, test_image, tmp_path):
        """Test resizing image without aspect ratio"""
        output_path = tmp_path / "resized.png"

        result = plugin.resize(
            test_image,
            str(output_path),
            (50, 75),
            keep_aspect_ratio=False
        )

        assert result == str(output_path)
        assert output_path.exists()

        # Check exact size
        img = Image.open(output_path)
        assert img.size == (50, 75)

    def test_crop(self, plugin, test_image, tmp_path):
        """Test cropping image"""
        output_path = tmp_path / "cropped.png"

        result = plugin.crop(
            test_image,
            str(output_path),
            (10, 10, 60, 60)
        )

        assert result == str(output_path)
        assert output_path.exists()

        # Check cropped size
        img = Image.open(output_path)
        assert img.size == (50, 50)

        # Check processed count
        assert plugin._state["processed_count"] == 1

    def test_enhance_brightness(self, plugin, test_image, tmp_path):
        """Test enhancing image brightness"""
        output_path = tmp_path / "enhanced.png"

        result = plugin.enhance(
            test_image,
            str(output_path),
            brightness=1.5
        )

        assert result == str(output_path)
        assert output_path.exists()
        assert plugin._state["processed_count"] == 1

    def test_enhance_all_parameters(self, plugin, test_image, tmp_path):
        """Test enhancing image with all parameters"""
        output_path = tmp_path / "enhanced.png"

        result = plugin.enhance(
            test_image,
            str(output_path),
            brightness=1.2,
            contrast=1.3,
            sharpness=1.1,
            color=0.9
        )

        assert result == str(output_path)
        assert output_path.exists()

    def test_convert_format_png_to_jpeg(self, plugin, test_image, tmp_path):
        """Test converting PNG to JPEG"""
        output_path = tmp_path / "converted.jpg"

        result = plugin.convert_format(
            test_image,
            str(output_path),
            format="JPEG"
        )

        assert result == str(output_path)
        assert output_path.exists()

        # Check format
        img = Image.open(output_path)
        assert img.format == "JPEG"

    def test_convert_format_rgba_to_jpeg(self, plugin, test_image_rgba, tmp_path):
        """Test converting RGBA to JPEG (should convert to RGB)"""
        output_path = tmp_path / "converted.jpg"

        result = plugin.convert_format(
            test_image_rgba,
            str(output_path),
            format="JPEG"
        )

        assert result == str(output_path)
        assert output_path.exists()

        # Check format and mode
        img = Image.open(output_path)
        assert img.format == "JPEG"
        assert img.mode == "RGB"

    def test_convert_format_auto_detect(self, plugin, test_image, tmp_path):
        """Test auto-detecting format from extension"""
        output_path = tmp_path / "converted.jpg"

        result = plugin.convert_format(
            test_image,
            str(output_path)
        )

        assert result == str(output_path)
        assert output_path.exists()

        # Check format
        img = Image.open(output_path)
        assert img.format == "JPEG"

    def test_apply_filter_blur(self, plugin, test_image, tmp_path):
        """Test applying BLUR filter"""
        output_path = tmp_path / "filtered.png"

        result = plugin.apply_filter(
            test_image,
            str(output_path),
            filter_type="BLUR"
        )

        assert result == str(output_path)
        assert output_path.exists()
        assert plugin._state["processed_count"] == 1

    def test_apply_filter_sharpen(self, plugin, test_image, tmp_path):
        """Test applying SHARPEN filter"""
        output_path = tmp_path / "filtered.png"

        result = plugin.apply_filter(
            test_image,
            str(output_path),
            filter_type="SHARPEN"
        )

        assert result == str(output_path)
        assert output_path.exists()

    def test_apply_filter_smooth(self, plugin, test_image, tmp_path):
        """Test applying SMOOTH filter"""
        output_path = tmp_path / "filtered.png"

        result = plugin.apply_filter(
            test_image,
            str(output_path),
            filter_type="SMOOTH"
        )

        assert result == str(output_path)
        assert output_path.exists()

    def test_apply_filter_edge_enhance(self, plugin, test_image, tmp_path):
        """Test applying EDGE_ENHANCE filter"""
        output_path = tmp_path / "filtered.png"

        result = plugin.apply_filter(
            test_image,
            str(output_path),
            filter_type="EDGE_ENHANCE"
        )

        assert result == str(output_path)
        assert output_path.exists()

    def test_apply_filter_invalid(self, plugin, test_image, tmp_path):
        """Test applying invalid filter"""
        output_path = tmp_path / "filtered.png"

        with pytest.raises(ValueError, match="Unknown filter type"):
            plugin.apply_filter(
                test_image,
                str(output_path),
                filter_type="INVALID"
            )

    def test_get_stats(self, plugin, test_image, tmp_path):
        """Test getting plugin statistics"""
        # Initial stats
        stats = plugin.get_stats()
        assert stats["processed_count"] == 0

        # Process some images
        output_path = tmp_path / "output.png"
        plugin.resize(test_image, str(output_path), (50, 50))

        stats = plugin.get_stats()
        assert stats["processed_count"] == 1

    def test_resize_error_handling(self, plugin, tmp_path):
        """Test error handling for resize"""
        with pytest.raises(Exception):
            plugin.resize(
                "nonexistent.png",
                str(tmp_path / "output.png"),
                (50, 50)
            )

    def test_crop_error_handling(self, plugin, tmp_path):
        """Test error handling for crop"""
        with pytest.raises(Exception):
            plugin.crop(
                "nonexistent.png",
                str(tmp_path / "output.png"),
                (0, 0, 50, 50)
            )

    def test_enhance_error_handling(self, plugin, tmp_path):
        """Test error handling for enhance"""
        with pytest.raises(Exception):
            plugin.enhance(
                "nonexistent.png",
                str(tmp_path / "output.png")
            )

    def test_convert_format_error_handling(self, plugin, tmp_path):
        """Test error handling for convert_format"""
        with pytest.raises(Exception):
            plugin.convert_format(
                "nonexistent.png",
                str(tmp_path / "output.png")
            )

    def test_apply_filter_error_handling(self, plugin, tmp_path):
        """Test error handling for apply_filter"""
        with pytest.raises(Exception):
            plugin.apply_filter(
                "nonexistent.png",
                str(tmp_path / "output.png")
            )

    def test_config_schema(self, plugin):
        """Test plugin configuration schema"""
        assert plugin.config_schema is not None
        assert len(plugin.config_schema.fields) == 3

        # Check field names
        field_names = [f.name for f in plugin.config_schema.fields]
        assert "default_format" in field_names
        assert "default_quality" in field_names
        assert "max_size" in field_names

    def test_config_default_values(self, plugin):
        """Test plugin configuration default values"""
        if plugin.config:
            assert plugin.config.get("default_format") == "PNG"
            assert plugin.config.get("default_quality") == 95
            assert plugin.config.get("max_size") == 4096

    def test_resize_without_config(self, test_image, tmp_path):
        """Test resizing without configuration"""
        plugin = ImageProcessor()
        plugin.config = None  # Simulate no config

        output_path = tmp_path / "resized"  # No extension

        result = plugin.resize(
            test_image,
            str(output_path),
            (50, 50)
        )

        assert result == str(output_path)
        assert Path(output_path).exists()

    def test_crop_without_config(self, test_image, tmp_path):
        """Test cropping without configuration"""
        plugin = ImageProcessor()
        plugin.config = None  # Simulate no config

        output_path = tmp_path / "cropped"  # No extension

        result = plugin.crop(
            test_image,
            str(output_path),
            (10, 10, 60, 60)
        )

        assert result == str(output_path)
        assert Path(output_path).exists()

    def test_enhance_without_config(self, test_image, tmp_path):
        """Test enhancing without configuration"""
        plugin = ImageProcessor()
        plugin.config = None  # Simulate no config

        output_path = tmp_path / "enhanced"  # No extension

        result = plugin.enhance(
            test_image,
            str(output_path),
            brightness=1.2
        )

        assert result == str(output_path)
        assert Path(output_path).exists()

    def test_convert_format_without_config(self, test_image, tmp_path):
        """Test converting format without configuration"""
        plugin = ImageProcessor()
        plugin.config = None  # Simulate no config

        output_path = tmp_path / "converted"  # No extension

        result = plugin.convert_format(
            test_image,
            str(output_path)
        )

        assert result == str(output_path)
        assert Path(output_path).exists()

    def test_apply_filter_without_config(self, test_image, tmp_path):
        """Test applying filter without configuration"""
        plugin = ImageProcessor()
        plugin.config = None  # Simulate no config

        output_path = tmp_path / "filtered"  # No extension

        result = plugin.apply_filter(
            test_image,
            str(output_path),
            filter_type="BLUR"
        )

        assert result == str(output_path)
        assert Path(output_path).exists()

