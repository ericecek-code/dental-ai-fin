"""
Jediný zdroj pravdy pre taxonómiu nálezov.

Používajú ho:
  - app.ml.detector  (bounding boxy, farby, severity v API odpovedi)
  - app.ml.reporter  (PDF report, slovenské labely a odporúčania)
  - frontend cez API (`label` = anglická trieda, `label_sk` = slovenský text)

Kľúče MUSIA zodpovedať `model.names` vo `weights/yolov8x_dental.pt` (31 tried).
Ak sa zmení model, zmení sa tento súbor — nikde inde.
"""

from typing import Dict

CLASSES: Dict[str, Dict[str, object]] = {
    "Caries": {
        "bgr": (0, 215, 255), "severity": "urgent",
        "label": "Caries", "label_sk": "Kaz", "severity_sk": "Okamžité riešenie",
        "recommendation_sk": "Okamžitá stomatologická konzultácia, prípadne vŕtanie.",
    },
    "Deep Caries": {
        "bgr": (0, 0, 255), "severity": "urgent",
        "label": "Deep Caries", "label_sk": "Hlboký kaz", "severity_sk": "Okamžité riešenie",
        "recommendation_sk": "Urgentná liečba – riziko zápalu nervu. Endodoncia môže byť potrebná.",
    },
    "Crown": {
        "bgr": (209, 206, 0), "severity": "watch",
        "label": "Crown", "label_sk": "Korunka", "severity_sk": "Sledovať",
        "recommendation_sk": "Pravidelná kontrola stavu korunky a podložia.",
    },
    "Implant": {
        "bgr": (180, 130, 0), "severity": "watch",
        "label": "Implant", "label_sk": "Implantát", "severity_sk": "Sledovať",
        "recommendation_sk": "Kontrola implantátu a peri-implantárnych tkanív.",
    },
    "Malaligned": {
        "bgr": (160, 80, 60), "severity": "watch",
        "label": "Malaligned", "label_sk": "Zlá poloha zuba", "severity_sk": "Sledovať",
        "recommendation_sk": "Ortodontické vyšetrenie, prípadne úprava.",
    },
    "Mandibular Canal": {
        "bgr": (255, 200, 180), "severity": "watch",
        "label": "Mandibular Canal", "label_sk": "Mandibulárny kanál", "severity_sk": "Sledovať",
        "recommendation_sk": "Informácia pre plánovanie chirurgických zákrokov.",
    },
    "Missing teeth": {
        "bgr": (160, 50, 60), "severity": "treat_soon",
        "label": "Missing teeth", "label_sk": "Chýbajúci zub", "severity_sk": "Ošetriť čoskoro",
        "recommendation_sk": "Náhrada chýbajúceho zuba – implantát alebo mostík.",
    },
    "Periapical lesion": {
        "bgr": (140, 20, 211), "severity": "urgent",
        "label": "Periapical lesion", "label_sk": "Periapikálna lézia", "severity_sk": "Okamžité riešenie",
        "recommendation_sk": "Urgentná liečba – endodoncia alebo extrakcia.",
    },
    "Retained root": {
        "bgr": (40, 60, 130), "severity": "treat_soon",
        "label": "Retained root", "label_sk": "Retinovaný koreň", "severity_sk": "Ošetriť čoskoro",
        "recommendation_sk": "Chirurgické odstránenie retinovaného koreňa.",
    },
    "Root Canal Treatment": {
        "bgr": (60, 140, 220), "severity": "watch",
        "label": "Root Canal Treatment", "label_sk": "Endodoncia", "severity_sk": "Sledovať",
        "recommendation_sk": "Kontrola endodontického ošetrenia (RTG kontrola).",
    },
    "Root Piece": {
        "bgr": (40, 40, 100), "severity": "treat_soon",
        "label": "Root Piece", "label_sk": "Koreňový fragment", "severity_sk": "Ošetriť čoskoro",
        "recommendation_sk": "Odstránenie koreňového zvyšku.",
    },
    "impacted tooth": {
        "bgr": (200, 100, 20), "severity": "treat_soon",
        "label": "impacted tooth", "label_sk": "Retinovaný zub", "severity_sk": "Ošetriť čoskoro",
        "recommendation_sk": "Chirurgické alebo ortodontické riešenie retinovaného zuba.",
    },
    "Impacted tooth": {
        "bgr": (200, 100, 20), "severity": "treat_soon",
        "label": "Impacted tooth", "label_sk": "Retinovaný zub", "severity_sk": "Ošetriť čoskoro",
        "recommendation_sk": "Chirurgické alebo ortodontické riešenie retinovaného zuba.",
    },
    "Filling": {
        "bgr": (220, 230, 240), "severity": "watch",
        "label": "Filling", "label_sk": "Plomba", "severity_sk": "Sledovať",
        "recommendation_sk": "Kontrola integrity plomby.",
    },
    "maxillary sinus": {
        "bgr": (230, 190, 140), "severity": "watch",
        "label": "maxillary sinus", "label_sk": "Čeľustná dutina", "severity_sk": "Sledovať",
        "recommendation_sk": "Posúdenie stavu maxilárneho sinu pred chirurgickým zákrokom.",
    },
    "Bone Loss": {
        "bgr": (90, 110, 160), "severity": "treat_soon",
        "label": "Bone Loss", "label_sk": "Úbytok kosti", "severity_sk": "Ošetriť čoskoro",
        "recommendation_sk": "Parodontologické vyšetrenie, prípadne regenerácia kosti.",
    },
    "Fracture teeth": {
        "bgr": (0, 0, 180), "severity": "urgent",
        "label": "Fracture teeth", "label_sk": "Zlomený zub", "severity_sk": "Okamžité riešenie",
        "recommendation_sk": "Urgentné ošetrenie – riziko straty zuba.",
    },
    "Permanent Teeth": {
        "bgr": (215, 235, 250), "severity": "watch",
        "label": "Permanent Teeth", "label_sk": "Trvalý zub", "severity_sk": "Sledovať",
        "recommendation_sk": "Bez patológie – rutinná kontrola.",
    },
    "Supra Eruption": {
        "bgr": (150, 120, 200), "severity": "treat_soon",
        "label": "Supra Eruption", "label_sk": "Preerupcia zuba", "severity_sk": "Ošetriť čoskoro",
        "recommendation_sk": "Ortodontické riešenie preerupovaného zuba.",
    },
    "TAD": {
        "bgr": (110, 160, 70), "severity": "watch",
        "label": "TAD", "label_sk": "Dočasný implantát (TAD)", "severity_sk": "Sledovať",
        "recommendation_sk": "Kontrola stability dočasného implantátu.",
    },
    "abutment": {
        "bgr": (170, 140, 90), "severity": "watch",
        "label": "abutment", "label_sk": "Abutment (nosný pilier)", "severity_sk": "Sledovať",
        "recommendation_sk": "Kontrola spojenia abutmentu a implantátu.",
    },
    "attrition": {
        "bgr": (140, 150, 165), "severity": "watch",
        "label": "attrition", "label_sk": "Obrus zuba", "severity_sk": "Sledovať",
        "recommendation_sk": "Sledovanie obrusu, prípadne ochrana skloviny.",
    },
    "bone defect": {
        "bgr": (70, 90, 140), "severity": "treat_soon",
        "label": "bone defect", "label_sk": "Defekt kosti", "severity_sk": "Ošetriť čoskoro",
        "recommendation_sk": "Chirurgické posúdenie kostného defektu.",
    },
    "gingival former": {
        "bgr": (190, 170, 210), "severity": "watch",
        "label": "gingival former", "label_sk": "Ďasnový formovač", "severity_sk": "Sledovať",
        "recommendation_sk": "Kontrola hojenia ďasna okolo formovača.",
    },
    "metal band": {
        "bgr": (200, 200, 200), "severity": "watch",
        "label": "metal band", "label_sk": "Kovová obruba", "severity_sk": "Sledovať",
        "recommendation_sk": "Kontrola fixácie kovovej obruby.",
    },
    "orthodontic brackets": {
        "bgr": (120, 120, 220), "severity": "watch",
        "label": "orthodontic brackets", "label_sk": "Ortodontické závesy", "severity_sk": "Sledovať",
        "recommendation_sk": "Kontrola ortodontického aparátu.",
    },
    "permanent retainer": {
        "bgr": (170, 170, 170), "severity": "watch",
        "label": "permanent retainer", "label_sk": "Fixný retainer", "severity_sk": "Sledovať",
        "recommendation_sk": "Kontrola fixného retaineru.",
    },
    "post - core": {
        "bgr": (100, 100, 160), "severity": "watch",
        "label": "post - core", "label_sk": "Čap a jadro", "severity_sk": "Sledovať",
        "recommendation_sk": "Kontrola čapu a jadra, prípadne RTG.",
    },
    "plating": {
        "bgr": (180, 180, 140), "severity": "watch",
        "label": "plating", "label_sk": "Dlaha", "severity_sk": "Sledovať",
        "recommendation_sk": "Kontrola dlahy a fixácie.",
    },
    "wire": {
        "bgr": (200, 200, 200), "severity": "watch",
        "label": "wire", "label_sk": "Drôt", "severity_sk": "Sledovať",
        "recommendation_sk": "Kontrola drôtovej fixácie.",
    },
    "Cyst": {
        "bgr": (40, 20, 130), "severity": "treat_soon",
        "label": "Cyst", "label_sk": "Cysta", "severity_sk": "Ošetriť čoskoro",
        "recommendation_sk": "Chirurgické odstránenie cysty, histologické vyšetrenie.",
    },
    "Root resorption": {
        "bgr": (130, 40, 60), "severity": "treat_soon",
        "label": "Root resorption", "label_sk": "Resorpcia koreňa", "severity_sk": "Ošetriť čoskoro",
        "recommendation_sk": "Sledovanie progresie, prípadne endodoncia.",
    },
    "Primary teeth": {
        "bgr": (200, 220, 240), "severity": "watch",
        "label": "Primary teeth", "label_sk": "Mliečne zuby", "severity_sk": "Sledovať",
        "recommendation_sk": "Sledovanie výmeny mliečnych zubov.",
    },
}

DEFAULT: Dict[str, object] = {
    "bgr": (127, 255, 0),
    "severity": "watch",
    "label": "Unknown",
    "label_sk": "Neznámy nález",
    "severity_sk": "Sledovať",
    "recommendation_sk": "Neznámy nález – odporúčaná klinická kontrola.",
}


def color_for(class_name: str) -> Dict[str, object]:
    """Vráti taxonomický záznam pre triedu (alebo DEFAULT pre neznámu)."""
    return CLASSES.get(class_name, DEFAULT)
