"""Odstránenie osobných údajov zo vstupnej snímky.

Cieľ: po nahratí RTG nesmie v systéme zostať nič, čo identifikuje pacienta —
EXIF/XMP/ICC metadáta, DICOM identifikačné tagy ani názov súboru.

Použitie:
    anon = anonymize_upload(raw_bytes, ".dcm")
    anon.data          # očistené bajty
    anon.suffix        # prípona očisteného súboru (raster -> .png)
    anon.removed       # zoznam odstránených metadát / tagov
"""

from __future__ import annotations

import io
import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

# DICOM tagy, ktoré priamo identifikujú pacienta alebo vyšetrenie.
# (VR "PN" sa čistí plošne — Person Name.)
DICOM_TAGS_TO_CLEAR = {
    "PatientName",
    "PatientID",
    "IssuerOfPatientID",
    "OtherPatientIDs",
    "OtherPatientIDsSequence",
    "PatientBirthDate",
    "PatientBirthTime",
    "PatientAddress",
    "PatientTelephoneNumbers",
    "PatientMotherBirthName",
    "PatientComments",
    "MedicalRecordLocator",
    "AccessionNumber",
    "StudyID",
    "InstitutionName",
    "InstitutionAddress",
    "InstitutionalDepartmentName",
    "ReferringPhysicianName",
    "PerformingPhysicianName",
    "PhysiciansOfRecord",
    "RequestingPhysician",
    "NameOfPhysiciansReadingStudy",
    "OperatorsName",
    "StationName",
    "DeviceSerialNumber",
    "StudyDescription",
    "SeriesDescription",
    "ProtocolName",
    "ImageComments",
    "AdmittingDiagnosesDescription",
    "RequestAttributesSequence",
    "ReferencedPatientSequence",
}

# Raster formáty: metadáta, ktoré bežne nesú osobnú stopu.
RASTER_META_KEYS = ("exif", "icc_profile", "xmp", "photoshop", "comment", "XML:com.adobe.xmp")


@dataclass
class AnonymizeResult:
    data: bytes
    suffix: str
    removed: list[str] = field(default_factory=list)
    ok: bool = True


def _anonymize_dicom(raw: bytes) -> AnonymizeResult | None:
    """Vymaže identifikačné DICOM tagy; pixely ostávajú nedotknuté."""
    try:
        import pydicom  # type: ignore
    except ImportError:
        logger.warning("pydicom nie je nainštalovaný — DICOM sa nepodarilo anonymizovať")
        return None

    try:
        dataset = pydicom.dcmread(io.BytesIO(raw))
    except Exception as exc:  # pragma: no cover - závisí od súboru
        logger.warning("DICOM sa nedá prečítať: %s", exc)
        return None

    removed: list[str] = []
    for elem in dataset.iterall():
        keyword = getattr(elem, "keyword", "") or str(elem.tag)
        if elem.VR == "PN" or keyword in DICOM_TAGS_TO_CLEAR:
            if elem.value not in (None, "", b""):
                removed.append(keyword)
            try:
                elem.value = ""
            except Exception:  # pragma: no cover - neštandardné tagy
                pass

    buffer = io.BytesIO()
    try:
        dataset.save_as(buffer, enforce_file_format=True)
    except TypeError:  # pydicom < 3
        buffer = io.BytesIO()
        dataset.save_as(buffer)
    except Exception as exc:  # pragma: no cover
        logger.warning("DICOM sa nedá zapísať: %s", exc)
        return None

    return AnonymizeResult(data=buffer.getvalue(), suffix=".dcm", removed=sorted(set(removed)))


def _anonymize_raster(raw: bytes) -> AnonymizeResult | None:
    """Prekóduje obrázok do PNG bez metadát (EXIF, XMP, ICC...)."""
    try:
        from PIL import Image
    except ImportError:  # pragma: no cover - Pillow je v requirements
        return None

    try:
        with Image.open(io.BytesIO(raw)) as image:
            removed = [k for k in image.info if k.lower() in RASTER_META_KEYS]
            if image.mode not in ("RGB", "L"):
                image = image.convert("RGB")
            output = io.BytesIO()
            image.save(output, format="PNG", optimize=False)
    except Exception as exc:
        logger.warning("Obrázok sa nedá prekódovať: %s", exc)
        return None

    return AnonymizeResult(
        data=output.getvalue(),
        suffix=".png",
        removed=sorted(set(removed or ["metadata"])),
    )


def anonymize_upload(raw: bytes, suffix: str) -> AnonymizeResult:
    """Vráti očistenú kópiu nahratého súboru.

    Pri DICOM sa mažú identifikačné tagy, pri rastrových formátoch sa obrázok
    prekóduje do PNG (tým zmiznú všetky metadáta). Ak sa očistenie nedá
    vykonať, vráti sa `ok=False` a pôvodné bajty — volajúci sa rozhodne.
    """
    suffix = (suffix or "").lower()
    result = _anonymize_dicom(raw) if suffix == ".dcm" else _anonymize_raster(raw)
    if result is None:
        return AnonymizeResult(data=raw, suffix=suffix or ".bin", ok=False)
    return result
