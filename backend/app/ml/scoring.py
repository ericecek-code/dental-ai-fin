"""Health score — jediná implementácia pre API aj PDF report.

Skóre je 0–100 (vyššie = zdravšie). API ho posiela ako 0.0–1.0
(`health_score`), PDF a UI ho zobrazujú ako 0–100.
"""

from typing import Dict, List

SEVERITY_WEIGHT = {"urgent": 30, "treat_soon": 15, "watch": 5}

SEVERITY_LABELS_SK = {
    "urgent": "Urgentné",
    "treat_soon": "Liečiť čoskoro",
    "watch": "Sledovať",
}


def compute_health(detections: List[Dict]) -> Dict:
    """Vráti {"score": 0–100, "breakdown": {...}, "total": n}."""
    score = 100
    breakdown = {"Urgentné": 0, "Liečiť čoskoro": 0, "Sledovať": 0}
    for det in detections:
        severity = det.get("severity", "watch")
        score -= SEVERITY_WEIGHT.get(severity, 5)
        label = SEVERITY_LABELS_SK.get(severity, severity)
        breakdown[label] = breakdown.get(label, 0) + 1
    return {
        "score": max(0, min(100, score)),
        "breakdown": breakdown,
        "total": len(detections),
    }


def health_score_fraction(detections: List[Dict]) -> float:
    """Skóre normalizované na 0.0–1.0 (formát API)."""
    return round(compute_health(detections)["score"] / 100.0, 2)
