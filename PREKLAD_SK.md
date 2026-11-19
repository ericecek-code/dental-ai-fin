# 🦷 Prekladové dvojice — Dental AI (EN → SK)

Tento súbor obsahuje všetky anglické reťazce, ktoré je potrebné preložiť do slovenčiny pre projekt Dental AI.  
Použite ho ako referenčnú tabuľku pri lokalizácii.

## 1. Detekčné triedy (YOLO model)

| Anglicky | Slovenčina (preložiť) | Poznámka |
|----------|----------------------|----------|
| Caries | Kaz | |
| Deep Caries | Hluboký kaz | |
| Crown | Korunka | |
| Implant | Implantát | |
| Malaligned | Nesprávne zarastený zub | |
| Mandibular Canal | Kanálika dolnej čeluste | |
| Missing teeth | Chýbajúce zuby | |
| Periapical lesion | Periapikálna lézia | |
| Retained root | Koreň | |
| Root Canal Treatment | Kanálková liečba | |
| Root Piece | Časť koreňa | |
| impacted tooth | Zadržaný zub | malé "i" |
| Impacted tooth | Zadržaný zub | veľké "I" |
| Filling | Plomba | |
| plating | Plátovanie | |
| wire | Drôt | |
| Cyst | Cysta | |
| Root resorption | Resorpcia koreňa | |
| Primary teeth | Mliečné zuby | |
| Unknown | Neznáma | default štítok |

## 2. Úroveň závažnosti (severity)

| Anglicky | Slovenčina (preložiť) | Použitie |
|----------|----------------------|----------|
| urgent | Okamžité riešenie | kritický nález |
| treat_soon | Ošetriť skoro | treba ošetriť v najbližšom čase |
| watch | Sledovať | len monitorovanie, no akutné riešenie nie je potrebné |
| normal | Normálne | bez nálezov |

## 3. UI reťazce (frontend)

| Anglicky | Slovenčina (preložiť) | Kde sa používa |
|----------|----------------------|----------------|
| Dental AI | Dental AI | hlavička aplikácie |
| RTG Analýza | RTG Analýza | podtitulok v navbar |
| Analýza RTG snímky | Analýza RTG snímky | nadpis dashboardu |
| Automatická detekcia kariésu, implantátov a patológií cez YOLOv8 | Automatická detekcia kariésu, implantátov a patológií cez YOLOv8 | popis dashboardu |
| Nahráť nový snímok | Nahrať nový snímok | tlačidlo |
| Reset | Reset | tlačidlo |
| Detekované nálezy | Detekované nálezy | štatistika |
| Health Score | Health Score | štatistika |
| Prahový filtr | Prahový filter | štatistika |
| Snímok | snímka | štatistika |
| Prehľad závažnosti | Prehľad závažnosti | panel závažnosti |
| Okamžité riešenie | Okamžité riešenie | odznaky závažnosti |
| Ošetriť skoro | Ošetriť skoro | odznaky závažnosti |
| Sledovať | Sledovať | odznaky závažnosti |
| Celkový health score | Celkový health score | merania |
| Pripravený na analýzu | Pripravený na analýzu | prázdny stav |
| Nahrajte panoramatický RTG snímok a Dental AI automaticky detekuje kaz, implantáty, cysty a inú patológiu. | Nahrajte panoramatický RTG snímok a Dental AI automaticky detekuje kaz, implantáty, cysty a inú patológiu. | prázdny stav |
| Kliknite pre nahratie RTG snímky | Kliknite pre nahratie RTG snímky | upload zóna |
| JPEG, PNG, DICOM • max 50 MB | JPEG, PNG, DICOM • max 50 MB | upload zóna |
| Súbor vybratý | Súbor vybratý | upload zóna (po výbere) |
| Odstrániť | Odstrániť | upload zóna (tlačidlo) |
| Nahrajte panoramatický RTG | Nahrajte panoramatický RTG | upload zóna (prázdny stav) |
| Kliknite alebo ťahajte sem snímku | Kliknite alebo ťahajte sem snímku | upload zóna (prázdny stav) |
| Kaz: | Kaz: | farebná legenda |
| Heatmapa: | Heatmapa: | farebná legenda |
| Pseudocolor: | Pseudocolor: | farebná legenda |
| Skorý kaz (0–30%) | Skorý kaz (0–30%) | farebná legenda |
| Stredný kaz (30–60%) | Stredný kaz (30–60%) | farebná legenda |
| Závažný kaz (60–100%) | Závažný kaz (60–100%) | farebná legenda |
| Nízka istota | Nízka istota | heatmapa legenda |
| Stredná istota | Stredná istota | heatmapa legenda |
| Vysoká istota | Vysoká istota | heatmapa legenda |
| Nízka hustota | Nízka hustota | pseudocolor legenda |
| Stredná hustota | Stredná hustota | pseudocolor legenda |
| Vysoká hustota | Vysoká hustota | pseudocolor legenda |
| Analýza zlyhala. Skúste znova alebo skontrolujte formát snímku. | Analýza zlyhala. Skúste znova alebo skontrolujte formát snímku. | chybové hlásenie |
| Neplatný typ súboru | Neplatný typ súboru | chybové hlásenie |
| Súbor je príliš veľký | Súbor je príliš veľký | chybové hlásenie |

## 4. Použitie v kóde

Preklady sú definované v:
- `backend/app/ml/detector.py` — `COLOR_MAP` slovník (kľúč `label` a `severity_sk`)
- `frontend/src/index.css` — štýly pre odznaky závažnosti
- `frontend/src/pages/Dashboard.tsx` — UI reťazce na obrazovke
- `frontend/src/components/ImageViewer/ColorLegend.tsx` — farbové legendy

---

**Tip:** Pri preklade zachovajte medicínsku terminológiu v slovenčine (napr. "kaz" namiesto "káriés", "koreň" namiesto "zostanený koreneň").