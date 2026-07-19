"""Gemini Vision Service for Dental X-ray Analysis."""

import cv2
import base64
import json
import time
import logging
import re
import requests
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent"
GEMINI_API_KEY = "AIzaSyD3CrVVRS6W2zDH0Lw64zvzgCkqxJLwMy0"

# FDI tooth numbering: quadrant * 10 + position
# Quadrant 1: upper right, 2: upper left, 3: lower left, 4: lower right
DENTAL_PROMPT = """Si skúsený stomatológ. Analyzuj túto panoramatickú RTG snímku (OPG).

Identifikuj KAŽDÝ nález a urči presné číslo zuba podle FDI notácie:
- 1. štvrťrok (horná pravá): zuby 11-18
- 2. štvrťrok (horná ľavá): zuby 21-28
- 3. štvrťrok (dolná ľavá): zuby 31-38
- 4. štvrťrok (dolná pravá): zuby 41-48

Pre každý nález uveď:
- label: typ nálezu (presne ako: Caries, Filling, Crown, Implant, Root Canal Treatment, Missing teeth, Periapical lesion, Retained root, Root Piece, Impacted tooth, Cyst, Bone loss)
- tooth: FDI číslo zuba (napr. "36", "17", "28")
- quadrant: číslo štvrťroku (1-4)
- confidence: 0.0-1.0
- severity: urgent / treat_soon / watch
- description: krátky popis v Slovenčine

VRÁŤ IBA TOTO JSON (bez ďalšieho textu):
{
  "findings": [
    {
      "label": "Caries",
      "tooth": "36",
      "quadrant": 3,
      "confidence": 0.85,
      "severity": "treat_soon",
      "description": "Stredný kaz na distálnej strane"
    }
  ],
  "overall_assessment": "Súhrnný posudok v Slovenčine"
}"""

BACKTICK_CODE_BLOCK = re.compile(r"```json\s*(\{.*?\})\s*```", re.DOTALL)
JSON_FIELD_TYPE = re.compile(r'"label"\s*:\s*"([^"]+)"')


def image_to_base64_jpeg(image_bgr, quality=85) -> str:
    encode_params = [cv2.IMWRITE_JPEG_QUALITY, quality]
    success, buffer = cv2.imencode(".jpg", image_bgr, encode_params)
    if not success:
        raise ValueError("Failed to encode image as JPEG")
    return base64.b64encode(buffer).decode("utf-8")


def _extract_findings_from_json(json_str: str):
    findings = []
    overall_assessment = ""
    try:
        parsed = json.loads(json_str)
        for f in parsed.get("findings", []):
            label = f.get("label", "Unknown")
            tooth = f.get("tooth", "")
            quadrant = f.get("quadrant", 0)
            findings.append({
                "label": label,
                "tooth": tooth,
                "quadrant": quadrant,
                "confidence": float(f.get("confidence", 0.5)),
                "severity": f.get("severity", "watch"),
                "description": f.get("description", ""),
                "bbox": None,
                # Map to YOLO-compatible format for comparison
                "location": f"tooth {tooth}" if tooth else f"quadrant {quadrant}",
            })
        overall_assessment = parsed.get("overall_assessment", "")
        return findings, overall_assessment
    except json.JSONDecodeError:
        pass

    # Try fixing truncated JSON
    try:
        fixed = json_str.rstrip().rstrip(",")
        open_b = fixed.count("{") - fixed.count("}")
        open_sq = fixed.count("[") - fixed.count("]")
        fixed += "]" * open_sq + "}" * open_b
        parsed = json.loads(fixed)
        for f in parsed.get("findings", []):
            label = f.get("label", "Unknown")
            tooth = f.get("tooth", "")
            quadrant = f.get("quadrant", 0)
            findings.append({
                "label": label,
                "tooth": tooth,
                "quadrant": quadrant,
                "confidence": float(f.get("confidence", 0.5)),
                "severity": f.get("severity", "watch"),
                "description": f.get("description", ""),
                "bbox": None,
                "location": f"tooth {tooth}" if tooth else f"quadrant {quadrant}",
            })
        overall_assessment = parsed.get("overall_assessment", "")
        return findings, overall_assessment
    except Exception:
        pass

    return findings, overall_assessment


def parse_gemini_response(response_text: str) -> Dict[str, Any]:
    findings = []
    overall_assessment = ""

    # Try code block first
    code_match = BACKTICK_CODE_BLOCK.search(response_text)
    if code_match:
        findings, overall_assessment = _extract_findings_from_json(code_match.group(1))
        if findings:
            return {"findings": findings, "overall_assessment": overall_assessment}

    # Try raw JSON
    i = response_text.find("{")
    j = response_text.rfind("}")
    if i != -1 and j > i:
        findings, overall_assessment = _extract_findings_from_json(response_text[i:j + 1])
        if findings:
            return {"findings": findings, "overall_assessment": overall_assessment}

    # Last resort: regex extract
    for m in JSON_FIELD_TYPE.finditer(response_text):
        label = m.group(1)
        rest = response_text[m.start():m.start() + 500]
        tooth_m = re.search(r'"tooth"\s*:\s*"([^"]+)"', rest)
        quad_m = re.search(r'"quadrant"\s*:\s*(\d+)', rest)
        conf_m = re.search(r'"confidence"\s*:\s*([\d.]+)', rest)
        sev_m = re.search(r'"severity"\s*:\s*"([^"]+)"', rest)
        desc_m = re.search(r'"description"\s*:\s*"([^"]+)"', rest)
        tooth = tooth_m.group(1) if tooth_m else ""
        findings.append({
            "label": label,
            "tooth": tooth,
            "quadrant": int(quad_m.group(1)) if quad_m else 0,
            "confidence": float(conf_m.group(1)) if conf_m else 0.5,
            "severity": sev_m.group(1) if sev_m else "watch",
            "description": desc_m.group(1) if desc_m else "",
            "bbox": None,
            "location": f"tooth {tooth}" if tooth else "Unknown",
        })

    return {"findings": findings, "overall_assessment": response_text[:500] if response_text else "No assessment"}


def match_yolo_gemini(yolo_detections: List[Dict], gemini_detections: List[Dict]) -> Dict[str, Any]:
    """Match YOLO and Gemini detections by tooth number and label for comparison."""
    matched = []
    yolo_only = []
    gemini_only = []

    # Build lookup: (label_normalized, tooth) -> detection
    def normalize_label(label: str) -> str:
        label = label.strip().lower()
        # Map common synonyms
        mapping = {
            "kaz": "caries", "deep caries": "caries",
            "plomba": "filling", "korunka": "crown",
            "implantát": "implant", "endodoncia": "root canal treatment",
            "periapikálna lézia": "periapical lesion",
            "chýbajúci zub": "missing teeth",
            "retinovaný zub": "impacted tooth",
            "retinovaný koreň": "retained root",
            "koreňový fragment": "root piece",
        }
        return mapping.get(label, label)

    def extract_tooth(det: Dict) -> str:
        # Try tooth field
        tooth = det.get("tooth", "")
        if tooth:
            return str(tooth).strip()
        # Try location field
        loc = det.get("location", "")
        m = re.search(r"(\d{2})", str(loc))
        if m:
            return m.group(1)
        return ""

    gemini_used = [False] * len(gemini_detections)

    for yolo in yolo_detections:
        y_label = normalize_label(yolo.get("label", ""))
        y_tooth = extract_tooth(yolo)

        best_match = None
        best_idx = -1
        for i, gem in enumerate(gemini_detections):
            if gemini_used[i]:
                continue
            g_label = normalize_label(gem.get("label", ""))
            g_tooth = extract_tooth(gem)

            if y_label == g_label and y_tooth and g_tooth and y_tooth == g_tooth:
                best_match = gem
                best_idx = i
                break
            elif y_label == g_label and not y_tooth and not g_tooth:
                best_match = gem
                best_idx = i
                break

        if best_match:
            gemini_used[best_idx] = True
            matched.append({
                "label": yolo.get("label", ""),
                "label_sk": yolo.get("label", ""),
                "tooth": y_tooth,
                "yolo_confidence": yolo.get("confidence", 0),
                "gemini_confidence": best_match.get("confidence", 0),
                "severity": yolo.get("severity", best_match.get("severity", "watch")),
                "description_yolo": "",
                "description_gemini": best_match.get("description", ""),
            })
        else:
            yolo_only.append({
                "label": yolo.get("label", ""),
                "tooth": y_tooth,
                "confidence": yolo.get("confidence", 0),
                "severity": yolo.get("severity", "watch"),
            })

    for i, gem in enumerate(gemini_detections):
        if not gemini_used[i]:
            gemini_only.append({
                "label": gem.get("label", ""),
                "tooth": extract_tooth(gem),
                "confidence": gem.get("confidence", 0),
                "severity": gem.get("severity", "watch"),
                "description": gem.get("description", ""),
            })

    return {
        "matched": matched,
        "yolo_only": yolo_only,
        "gemini_only": gemini_only,
        "summary": {
            "yolo_count": len(yolo_detections),
            "gemini_count": len(gemini_detections),
            "matched_count": len(matched),
            "yolo_only_count": len(yolo_only),
            "gemini_only_count": len(gemini_only),
        }
    }


def analyze_xray_with_gemini(image_bgr, custom_prompt=None, temperature=0.3, max_retries=3):
    start_time = time.time()
    result = {
        "gemini_raw_text": "",
        "gemini_detections": [],
        "overall_assessment": "",
        "success": False,
        "error": None,
        "processing_time_ms": 0,
    }

    try:
        b64_image = image_to_base64_jpeg(image_bgr)
        prompt = custom_prompt or DENTAL_PROMPT

        payload = {
            "contents": [{"parts": [{"text": prompt}, {"inline_data": {"mime_type": "image/jpeg", "data": b64_image}}]}],
            "generationConfig": {"temperature": temperature, "maxOutputTokens": 8192},
        }

        url = f"{GEMINI_API_URL}?key={GEMINI_API_KEY}"

        last_error = None
        for attempt in range(max_retries):
            try:
                response = requests.post(url, json=payload, timeout=120)
                if response.status_code == 429:
                    wait = (2 ** attempt) * 5
                    logger.warning(f"Gemini 429, retry {attempt + 1}/{max_retries} in {wait}s")
                    time.sleep(wait)
                    continue
                response.raise_for_status()
                break
            except requests.exceptions.Timeout:
                last_error = "timeout"
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
                raise
        else:
            result["error"] = f"Gemini API: {last_error or 'rate limited'}"
            return result

        api_result = response.json()
        raw_text = ""
        if "candidates" in api_result and api_result["candidates"]:
            candidate = api_result["candidates"][0]
            if "content" in candidate and "parts" in candidate["content"]:
                for part in candidate["content"]["parts"]:
                    if "text" in part:
                        raw_text += part["text"]

        result["gemini_raw_text"] = raw_text
        if not raw_text:
            result["error"] = "Gemini returned empty response"
            return result

        parsed = parse_gemini_response(raw_text)
        result["gemini_detections"] = parsed["findings"]
        result["overall_assessment"] = parsed["overall_assessment"]
        result["success"] = True

    except requests.exceptions.Timeout:
        result["error"] = "Gemini API timeout after retries"
    except requests.exceptions.RequestException as e:
        result["error"] = f"Gemini API error: {str(e)}"
    except Exception as e:
        result["error"] = f"Unexpected error: {str(e)}"
    finally:
        result["processing_time_ms"] = round((time.time() - start_time) * 1000, 1)

    return result


async def analyze_xray_with_gemini_async(image_bgr, custom_prompt=None, temperature=0.3):
    import asyncio
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, lambda: analyze_xray_with_gemini(image_bgr, custom_prompt, temperature))
