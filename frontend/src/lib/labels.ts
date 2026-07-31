/**
 * Slovenské preklady tried (YOLO class names z backendu).
 * Zdroj: backend/app/ml/detector.py -> COLOR_MAP[*].label
 *
 * Ak trieda nie je v mape, vráti sa originál (anglický label) —
 * takže ak sa v modeli objaví nová trieda, UI ju neskrížime.
 */
export const CLASS_LABELS_SK: Record<string, string> = {
  // Kaz a poskodenie
  'Caries':                 'Kaz',
  'Deep Caries':            'Hlboký kaz',

  // Rekonstrukcie
  'Crown':                  'Korunka',
  'Filling':                'Plomba',
  'Implant':                'Implantát',
  'Root Canal Treatment':   'Endodoncia',

  // Anomalie
  'Malaligned':             'Zlá poloha zuba',
  'Mandibular Canal':       'Mandibulárny kanál',
  'Missing teeth':          'Chýbajúci zub',
  'Periapical lesion':      'Periapikálna lézia',
  'Retained root':          'Retinovaný koreň',
  'Root Piece':             'Koreňový fragment',
  'Impacted tooth':         'Retinovaný zub',
  'impacted tooth':         'Retinovaný zub',
  'Root resorption':        'Resorpcia koreňa',

  // Vyvoj a dutiny
  'Cyst':                   'Cysta',
  'Primary teeth':          'Mliečne zuby',

  // Ortodontia
  'wire':                   'Drôt',
  'plating':                'Dlaha',
};

/**
 * Bezpecne prelozi triedu do slovenciny.
 * Fallback: originálny anglický label (case-insensitive, trim).
 */
export function translateClass(rawLabel: string): string {
  if (!rawLabel) return '';
  const key = rawLabel.trim();
  return CLASS_LABELS_SK[key] ?? CLASS_LABELS_SK[key.toLowerCase()] ?? rawLabel;
}

/**
 * Slovenské preklady severity (z backendu).
 */
export const SEVERITY_LABELS_SK: Record<string, string> = {
  urgent:     '🚨 Urgentné',
  treat_soon: '⚠️ Liečiť čoskoro',
  watch:      '👀 Sledovať',
};

export function translateSeverity(raw: string): string {
  return SEVERITY_LABELS_SK[raw] ?? raw;
}

/**
 * Stav merania (normalita nálezov).
 */
export const MEASUREMENT_STATUS_SK: Record<string, string> = {
  normal:   '✅ Normálny',
  mild:     '🟡 Mierny',
  moderate: '🟠 Stredný',
  severe:   '🔴 Závažný',
};

export function translateMeasurementStatus(raw: string): string {
  return MEASUREMENT_STATUS_SK[raw] ?? raw;
}

/**
 * Export labels.
 */
export const EXPORT_LABELS_SK = {
  json: 'Stiahnuť JSON',
  csv: 'Stiahnuť CSV',
  pdf: 'Stiahnuť PDF report',
} as const;

/**
 * Comparison view labels.
 */
export const COMPARISON_LABELS_SK = {
  original: 'Originál',
  enhanced: 'Vylepšená',
  sliderHint: 'Posuňte delič pre porovnanie originálu a vylepšenej snímky',
} as const;
