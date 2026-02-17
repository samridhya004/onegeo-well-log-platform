import io
import lasio
from sqlalchemy.orm import Session
from app.models.well import Well
from app.models.curve import Curve
from app.models.measurement import Measurement
from app.services.s3_service import upload_file_to_s3


def ingest_las_file(db: Session, file):
    """
    Handles full ingestion:
    - Duplicate check
    - Upload to S3
    - Parse LAS
    - Insert Well, Curves, Measurements
    """

    filename = file.filename

    # Duplicate check
    existing = db.query(Well).filter(Well.original_filename == filename).first()
    if existing:
        return {
            "duplicate": True,
            "well_id": existing.id,
            "well_name": existing.name,
            "message": "File already uploaded."
        }

    # Read file content (bytes)
    file_bytes = file.file.read()

    if not file_bytes:
        raise ValueError("Uploaded file is empty.")

    # Upload to S3 (bytes)
    upload_file_to_s3(io.BytesIO(file_bytes), filename)

    # Decode bytes to string for LAS parsing
    file_text = file_bytes.decode("utf-8", errors="ignore")
    las = lasio.read(io.StringIO(file_text))

    # Create Well
    well_name = filename
    if hasattr(las.well, "WELL") and las.well.WELL.value:
        well_name = las.well.WELL.value

    well = Well(
        name=well_name,
        original_filename=filename,
    )

    db.add(well)
    db.flush()

    # Depth index
    depth_values = las.index

    # Create Curves (exclude depth)
    curve_objects = []

    depth_mnemonic = las.curves[0].mnemonic

    for curve in las.curves:
        if curve.mnemonic == depth_mnemonic:
            continue


        curve_obj = Curve(
            well_id=well.id,
            mnemonic=curve.mnemonic,
            unit=curve.unit,
            description=curve.descr,
        )
        db.add(curve_obj)
        db.flush()
        curve_objects.append(curve_obj)

    # Bulk insert measurements
    measurements = []

    for curve_obj in curve_objects:
        values = las[curve_obj.mnemonic]

        for depth, value in zip(depth_values, values):
            measurements.append(
                Measurement(
                    curve_id=curve_obj.id,
                    depth=float(depth),
                    value=float(value) if value is not None else None,
                )
            )

    db.bulk_save_objects(measurements)
    db.commit()

    return {
        "well_id": well.id,
        "well_name": well.name,
        "curves_ingested": len(curve_objects),
        "measurements_inserted": len(measurements),
    }
