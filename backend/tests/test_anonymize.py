"""Testy anonymizácie vstupných snímok (osobné údaje)."""

import io

import pytest

from app.ml.anonymize import anonymize_upload


def _jpeg_with_exif() -> bytes:
    from PIL import Image

    image = Image.new("RGB", (48, 32), (130, 130, 130))
    exif = image.getexif()
    exif[0x010F] = "Canon"                     # Make
    exif[0x0110] = "EOS 5D"                    # Model
    exif[0x013B] = "MUDr. Ján Novák"           # Artist = meno lekára
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", exif=exif)
    return buffer.getvalue()


class TestRasterAnonymization:
    def test_exif_is_removed(self):
        raw = _jpeg_with_exif()
        result = anonymize_upload(raw, ".jpg")

        assert result.ok is True
        assert result.suffix == ".png"
        assert "exif" in result.removed

        from PIL import Image

        cleaned = Image.open(io.BytesIO(result.data))
        assert cleaned.format == "PNG"
        assert not cleaned.getexif(), "EXIF musí byť prázdny"
        assert "exif" not in cleaned.info

    def test_pixels_are_preserved(self):
        from PIL import Image

        raw = _jpeg_with_exif()
        before = Image.open(io.BytesIO(raw)).convert("RGB").getpixel((10, 10))
        after = Image.open(io.BytesIO(anonymize_upload(raw, ".jpg").data)).getpixel((10, 10))

        # JPEG -> PNG je bezstratový pre už dekódované pixely
        assert before == after

    def test_corrupted_file_is_reported(self):
        result = anonymize_upload(b"not an image", ".jpg")
        assert result.ok is False
        assert result.data == b"not an image"


class TestDicomAnonymization:
    """DICOM: identifikačné tagy musia zmiznúť, pixely ostať."""

    @pytest.fixture()
    def dicom_bytes(self):
        pydicom = pytest.importorskip("pydicom")
        from pydicom.dataset import Dataset, FileMetaDataset
        from pydicom.uid import ExplicitVRLittleEndian, generate_uid
        import numpy as np

        meta = FileMetaDataset()
        meta.MediaStorageSOPClassUID = generate_uid()
        meta.MediaStorageSOPInstanceUID = generate_uid()
        meta.TransferSyntaxUID = ExplicitVRLittleEndian

        ds = Dataset()
        ds.file_meta = meta
        ds.SOPClassUID = meta.MediaStorageSOPClassUID
        ds.SOPInstanceUID = meta.MediaStorageSOPInstanceUID
        ds.PatientName = "Novák Ján"
        ds.PatientID = "1234567890"
        ds.PatientBirthDate = "19700101"
        ds.InstitutionName = "Klinika Bratislava"
        ds.ReferringPhysicianName = "MUDr. Nováková"
        ds.Rows, ds.Columns = 8, 8
        ds.SamplesPerPixel = 1
        ds.PhotometricInterpretation = "MONOCHROME2"
        ds.BitsAllocated = ds.BitsStored = 8
        ds.HighBit = 7
        ds.PixelRepresentation = 0
        ds.PixelData = (np.full((8, 8), 128, dtype=np.uint8)).tobytes()

        buffer = io.BytesIO()
        try:
            ds.save_as(buffer, enforce_file_format=True)
        except TypeError:  # pydicom < 3
            ds.save_as(buffer)
        return buffer.getvalue()

    def test_identifying_tags_are_blanked(self, dicom_bytes):
        pydicom = pytest.importorskip("pydicom")

        result = anonymize_upload(dicom_bytes, ".dcm")
        assert result.ok is True
        assert result.suffix == ".dcm"

        cleaned = pydicom.dcmread(io.BytesIO(result.data))
        assert cleaned.PatientName == ""
        assert cleaned.PatientID == ""
        assert cleaned.PatientBirthDate == ""
        assert cleaned.InstitutionName == ""
        assert cleaned.ReferringPhysicianName == ""
        # pixely ostávajú (klinická časť snímky sa nesmie zmeniť)
        assert cleaned.Rows == 8 and cleaned.Columns == 8

        for tag in ("PatientName", "PatientID", "PatientBirthDate",
                    "InstitutionName", "ReferringPhysicianName"):
            assert tag in result.removed


class TestAnalyzePrivacy:
    def test_upload_filename_is_anonymized_and_upload_deleted(self, client):
        from app.api.routes.analyze import UPLOAD_DIR

        raw = _jpeg_with_exif()
        response = client.post(
            "/analyze/",
            files={"file": ("Novak_Jozef_rtg.jpg", raw, "image/jpeg")},
        )
        assert response.status_code == 200

        body = response.json()
        job_id = body["job_id"]
        assert body["privacy"]["anonymized"] is True
        assert body["filename"] == f"{job_id}.png"
        assert "Novak" not in body["filename"]

        leftovers = list(UPLOAD_DIR.glob(f"{job_id}*"))
        assert leftovers == [], f"na disku zostal surovy upload: {leftovers}"
