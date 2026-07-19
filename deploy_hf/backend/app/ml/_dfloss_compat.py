"""Monkey-patch DFLoss into ultralytics.utils.loss if missing.

The dental YOLO model was trained with a custom DFLoss (Distribution Focal Loss).
Some ultralytics versions expose it, others don't.  This shim guarantees it exists
so that torch.load() can deserialise the .pt weights.
"""

def patch_dfloss():
    """Install DFLoss into ultralytics.utils.loss if absent."""
    try:
        import torch
        import torch.nn as nn
        import ultralytics.utils.loss as loss_mod

        if hasattr(loss_mod, "DFLoss"):
            return  # already present – nothing to do

        class DFLoss(nn.Module):
            """Distribution Focal Loss (DFL) – simplified reconstruction."""

            def __init__(self, reg_max: int = 16):
                super().__init__()
                self.reg_max = reg_max
                self.device = "cpu"

            def forward(self, pred, target):
                # Placeholder: computes smooth-L1-like loss over distribution
                target = target.clamp(0, self.reg_max - 1)
                loss = torch.nn.functional.smooth_l1_loss(
                    pred.float(), target.float(), reduction="mean"
                )
                return loss

        loss_mod.DFLoss = DFLoss
        print("[compat] DFLoss patch installed")

    except Exception as e:
        print(f"[compat] DFLoss patch skipped: {e}")


# Auto-patch on import
patch_dfloss()
