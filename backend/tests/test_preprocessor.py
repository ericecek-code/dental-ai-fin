"""Tests for the image preprocessing module (ImageEnhancer)."""

import numpy as np
import pytest


class TestImageEnhancer:
    """Verify the image enhancement pipeline."""

    def test_enhance_returns_dict_keys(self, sample_image_array):
        """enhance() should return dict with 'original', 'enhanced', 'enhancement_metrics'."""
        from app.ml.preprocessor import ImageEnhancer
        enhancer = ImageEnhancer()
        result = enhancer.enhance(sample_image_array)
        assert "original" in result
        assert "enhanced" in result
        assert "enhancement_metrics" in result

    def test_enhance_preserves_original(self, sample_image_array):
        """enhance() should not modify the original image."""
        from app.ml.preprocessor import ImageEnhancer
        enhancer = ImageEnhancer()
        original_copy = sample_image_array.copy()
        result = enhancer.enhance(sample_image_array)
        np.testing.assert_array_equal(result["original"], original_copy)

    def test_enhanced_is_bgr(self, sample_image_array):
        """Enhanced output should be a 3-channel BGR image."""
        from app.ml.preprocessor import ImageEnhancer
        enhancer = ImageEnhancer()
        result = enhancer.enhance(sample_image_array)
        enhanced = result["enhanced"]
        assert enhanced.ndim == 3
        assert enhanced.shape[2] == 3

    def test_upscale_small_images(self, tiny_image_bytes):
        """Images smaller than 1024px should be upscaled."""
        import cv2
        from app.ml.preprocessor import ImageEnhancer
        enhancer = ImageEnhancer()
        img = cv2.imdecode(np.frombuffer(tiny_image_bytes, np.uint8), cv2.IMREAD_COLOR)
        result = enhancer.enhance(img)
        h, w = result["enhanced"].shape[:2]
        assert max(h, w) >= 1024, f"Expected upscaled min dim >= 1024, got {max(h, w)}"

    def test_large_images_not_upscaled(self, large_image_bytes):
        """Images >= 1024px should keep their original dimensions."""
        import cv2
        from app.ml.preprocessor import ImageEnhancer
        enhancer = ImageEnhancer()
        img = cv2.imdecode(np.frombuffer(large_image_bytes, np.uint8), cv2.IMREAD_COLOR)
        result = enhancer.enhance(img)
        h, w = result["enhanced"].shape[:2]
        assert h == img.shape[0] and w == img.shape[1]

    def test_enhancement_metrics_structure(self, sample_image_array):
        """enhancement_metrics should contain psnr, ssim, contrast_improvement."""
        from app.ml.preprocessor import ImageEnhancer
        enhancer = ImageEnhancer()
        result = enhancer.enhance(sample_image_array)
        metrics = result["enhancement_metrics"]
        assert "psnr" in metrics
        assert "ssim" in metrics
        assert "contrast_improvement" in metrics


class TestCLAHE:
    """Test the CLAHE static method directly."""

    def test_apply_clahe_returns_bgr(self, sample_image_array):
        """apply_clahe should return a 3-channel BGR image."""
        from app.ml.preprocessor import ImageEnhancer
        result = ImageEnhancer.apply_clahe(sample_image_array)
        assert result.ndim == 3
        assert result.shape[2] == 3

    def test_apply_clahe_preserves_dimensions(self, sample_image_array):
        """apply_clahe should not change image dimensions."""
        from app.ml.preprocessor import ImageEnhancer
        result = ImageEnhancer.apply_clahe(sample_image_array)
        assert result.shape[:2] == sample_image_array.shape[:2]

    def test_apply_clahe_custom_params(self, sample_image_array):
        """apply_clahe with custom clipLimit and tileGridSize should work."""
        from app.ml.preprocessor import ImageEnhancer
        result = ImageEnhancer.apply_clahe(sample_image_array, clipLimit=2.0, tileGridSize=(4, 4))
        assert result.shape == sample_image_array.shape


class TestBilateralFilter:
    """Test the bilateral filter static method."""

    def test_bilateral_preserves_dimensions(self, sample_image_array):
        """apply_bilateral_filter should keep image dimensions."""
        from app.ml.preprocessor import ImageEnhancer
        result = ImageEnhancer.apply_bilateral_filter(sample_image_array)
        assert result.shape == sample_image_array.shape

    def test_bilateral_is_bgr(self, sample_image_array):
        """apply_bilateral_filter should return BGR image."""
        from app.ml.preprocessor import ImageEnhancer
        result = ImageEnhancer.apply_bilateral_filter(sample_image_array)
        assert result.ndim == 3


class TestPseudocolor:
    """Test the pseudocolor static method."""

    def test_pseudocolor_returns_bgr(self, sample_image_array):
        """apply_pseudocolor should return a 3-channel image."""
        from app.ml.preprocessor import ImageEnhancer
        result = ImageEnhancer.apply_pseudocolor(sample_image_array)
        assert result.ndim == 3
        assert result.shape[2] == 3

    def test_pseudocolor_preserves_dimensions(self, sample_image_array):
        """apply_pseudocolor should keep image dimensions."""
        from app.ml.preprocessor import ImageEnhancer
        result = ImageEnhancer.apply_pseudocolor(sample_image_array)
        assert result.shape[:2] == sample_image_array.shape[:2]


class TestMorphologicalCariesEnhance:
    """Test the morphological caries enhancement."""

    def test_morphological_preserves_shape(self, sample_image_array):
        """apply_morphological_caries_enhance should keep image shape."""
        from app.ml.preprocessor import ImageEnhancer
        result = ImageEnhancer.apply_morphological_caries_enhance(sample_image_array)
        assert result.shape == sample_image_array.shape

    def test_morphological_enhances_dark_regions(self):
        """Dark regions in the image should be enhanced (brighter after black-hat)."""
        import cv2
        from app.ml.preprocessor import ImageEnhancer
        # Create image with a dark spot in the center
        img = np.ones((64, 64, 3), dtype=np.uint8) * 200
        cv2.circle(img, (32, 32), 10, (50, 50, 50), -1)
        result = ImageEnhancer.apply_morphological_caries_enhance(img)
        # The center dark spot should be brighter in the result
        center_orig = img[32, 32].mean()
        center_result = result[32, 32].mean()
        assert center_result >= center_orig
