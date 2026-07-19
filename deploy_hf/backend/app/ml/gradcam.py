"""Grad-CAM heatmap generator for YOLO dental model."""
import numpy as np
import cv2
import torch


class GradCAMGenerator:
    def __init__(self, detector):
        self.detector = detector
        self._activations = None
        self._gradients = None
        self._hook_handles = []

    def _register_hooks(self):
        """Register forward/backward hooks on the last convolutional layer."""
        model = self.detector.model.model
        # Find last Conv2d layer
        last_conv = None
        for module in model.modules():
            if isinstance(module, torch.nn.Conv2d):
                last_conv = module
        if last_conv is None:
            return False

        def forward_hook(module, input, output):
            self._activations = output.detach()

        def backward_hook(module, grad_input, grad_output):
            self._gradients = grad_output[0].detach()

        self._hook_handles.append(last_conv.register_forward_hook(forward_hook))
        self._hook_handles.append(last_conv.register_full_backward_hook(backward_hook))
        return True

    def generate(self, image: np.ndarray, class_id: int, target_size=None):
        """Generate Grad-CAM heatmap for a specific class."""
        if self.detector.model is None:
            self.detector.load()

        # Register hooks
        self._register_hooks()

        # Preprocess image for model
        model = self.detector.model.model
        model.eval()

        # Prepare input tensor
        img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        img_resized = cv2.resize(img_rgb, (640, 640))
        tensor = torch.from_numpy(img_resized).permute(2, 0, 1).float().unsqueeze(0) / 255.0
        tensor = tensor.to(next(model.parameters()).device)

        # Forward pass
        tensor.requires_grad_(True)
        output = model(tensor)

        # Backward pass for target class
        if isinstance(output, (list, tuple)):
            output = output[0]
        # For YOLO, we need to target specific detection
        model.zero_grad()
        if output.requires_grad:
            output[:, :, class_id].sum().backward()

        # Generate heatmap
        if self._activations is None or self._gradients is None:
            self._cleanup_hooks()
            return None

        weights = self._gradients.mean(dim=(2, 3), keepdim=True)
        cam = (weights * self._activations).sum(dim=1, keepdim=True)
        cam = torch.nn.functional.relu(cam)

        # Normalize
        cam = cam - cam.min()
        if cam.max() > 0:
            cam = cam / cam.max()

        # Resize to original image size
        cam_np = cam.squeeze().cpu().numpy()
        if target_size:
            cam_np = cv2.resize(cam_np, (target_size[1], target_size[0]))
        else:
            cam_np = cv2.resize(cam_np, (image.shape[1], image.shape[0]))

        self._cleanup_hooks()
        return cam_np

    def generate_for_detections(self, image: np.ndarray, detections: list):
        """Generate heatmaps for all detections and return a combined heatmap."""
        h, w = image.shape[:2]
        combined_heatmap = np.zeros((h, w), dtype=np.float32)

        for det in detections:
            class_id = det.get("class_id", 0)
            try:
                heatmap = self.generate(image, class_id, target_size=(h, w))
                if heatmap is not None:
                    # Weight by confidence
                    combined_heatmap += heatmap * det.get("confidence", 0.5)
            except Exception:
                continue

        if combined_heatmap.max() > 0:
            combined_heatmap = combined_heatmap / combined_heatmap.max()

        return combined_heatmap

    def _cleanup_hooks(self):
        for handle in self._hook_handles:
            handle.remove()
        self._hook_handles = []
        self._activations = None
        self._gradients = None

    @staticmethod
    def apply_colormap(heatmap: np.ndarray, colormap=cv2.COLORMAP_INFERNO):
        """Apply colormap to heatmap and return BGR image."""
        heatmap_uint8 = (heatmap * 255).astype(np.uint8)
        colored = cv2.applyColorMap(heatmap_uint8, colormap)
        return colored

    @staticmethod
    def overlay_heatmap(image: np.ndarray, heatmap: np.ndarray, alpha: float = 0.4):
        """Overlay heatmap on original image."""
        colored = GradCAMGenerator.apply_colormap(heatmap)
        overlay = cv2.addWeighted(image, 1 - alpha, colored, alpha, 0)
        return overlay
