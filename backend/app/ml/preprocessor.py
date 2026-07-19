from typing import Dict
import cv2
import numpy as np


class ImageEnhancer:
    """Image enhancement pipeline for dental X-ray analysis."""

    @staticmethod
    def apply_clahe(image: np.ndarray, clipLimit: float = 3.0,
                    tileGridSize: tuple = (8, 8)) -> np.ndarray:
        """Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
        for subtle caries enhancement."""
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=clipLimit, tileGridSize=tileGridSize)
        l = clahe.apply(l)
        lab = cv2.merge([l, a, b])
        return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)

    @staticmethod
    def apply_bilateral_filter(image: np.ndarray, d: int = 9,
                               sigmaColor: float = 75.0,
                               sigmaSpace: float = 75.0) -> np.ndarray:
        """Apply bilateral filter for noise reduction without edge loss."""
        return cv2.bilateralFilter(image, d, sigmaColor, sigmaSpace)

    @staticmethod
    def apply_pseudocolor(image: np.ndarray,
                          colormap: int = cv2.COLORMAP_BONE) -> np.ndarray:
        """Apply false color mapping for density visualization."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return cv2.applyColorMap(gray, colormap)

    @staticmethod
    def apply_morphological_caries_enhance(image: np.ndarray) -> np.ndarray:
        """Black-hat morphological operation to extract dark carious regions.

        Black-hat reveals small dark objects on a lighter background,
        which is ideal for detecting carious lesions in dental X-rays.
        """
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
        # Black-hat = closing - original; highlights dark spots
        blackhat = cv2.morphologyEx(image, cv2.MORPH_BLACKHAT, kernel)
        # Merge the black-hat back with the original for visibility
        enhanced = cv2.add(image, blackhat)
        return enhanced

    def enhance(self, image: np.ndarray) -> dict:
        """Full enhancement pipeline with CLAHE as default preprocessing step."""
        original = image.copy()
        enhanced = image.copy()

        # Step 1: CLAHE for subtle caries enhancement
        enhanced = self.apply_clahe(enhanced, clipLimit=3.0, tileGridSize=(8, 8))

        # Step 2: Bilateral filter – noise reduction without edge loss
        enhanced = self.apply_bilateral_filter(enhanced, d=9, sigmaColor=75, sigmaSpace=75)

        # Step 3: Morphological caries enhancement
        enhanced = self.apply_morphological_caries_enhance(enhanced)

        # Step 4: Upscale small images for better detection
        h, w = enhanced.shape[:2]
        if max(h, w) < 1024:
            scale = 1024 / max(h, w)
            enhanced = cv2.resize(
                enhanced,
                (int(w * scale), int(h * scale)),
                interpolation=cv2.INTER_CUBIC,
            )

        return {
            "original": original,
            "enhanced": enhanced,
            "enhancement_metrics": {
                "psnr": 0.0,
                "ssim": 0.0,
                "contrast_improvement": 0.0,
            },
        }
