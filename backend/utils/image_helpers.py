import io
import logging

logger = logging.getLogger(__name__)


class ImageHelper:
    """Utility functions for image processing."""

    @staticmethod
    def compress_image(image_data: bytes, max_size: int = 1024 * 1024, quality: int = 85) -> bytes:
        """Compress image to reduce size for faster API calls."""
        try:
            from PIL import Image

            img = Image.open(io.BytesIO(image_data))

            # Resize if very large
            max_dim = 1280
            if img.width > max_dim or img.height > max_dim:
                img.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)

            # Convert to RGB if needed
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')

            buffer = io.BytesIO()
            img.save(buffer, format='JPEG', quality=quality, optimize=True)
            buffer.seek(0)
            return buffer.read()

        except Exception as e:
            logger.error(f"Image compression failed: {e}")
            return image_data

    @staticmethod
    def validate_image(image_data: bytes) -> bool:
        """Check if the data is a valid image."""
        try:
            from PIL import Image
            img = Image.open(io.BytesIO(image_data))
            img.verify()
            return True
        except Exception:
            return False