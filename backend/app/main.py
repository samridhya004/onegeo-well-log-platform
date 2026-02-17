from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import List

from app.db.database import engine, get_db
from app.db.base import Base

from app.models.well import Well
from app.models.curve import Curve
from app.models.measurement import Measurement

from app.schemas.well_schema import WellResponse
from app.schemas.curve_schema import CurveResponse
from app.schemas.measurement_schema import MeasurementResponse

from app.services.ingestion_service import ingest_las_file
from app.services.interpretation_service import interpret_curve

from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="OneGeo Well Log Platform")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def create_tables():
    Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"message": "OneGeo backend is running"}


@app.get("/health/db")
def check_db():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return {"database": "connected"}
    except Exception as e:
        return {"database": "error", "details": str(e)}


# Upload LAS
@app.post("/api/wells/upload")
async def upload_well(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    if not file.filename.lower().endswith(".las"):
        raise HTTPException(status_code=400, detail="Only LAS files are allowed.")

    try:
        result = ingest_las_file(db, file)

        if result.get("duplicate"):
            return result
        
        return result
    
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# List Wells
@app.get("/api/wells", response_model=List[WellResponse])
def list_wells(db: Session = Depends(get_db)):
    wells = db.query(Well).all()
    return wells


# List Curves For a Well
@app.get("/api/wells/{well_id}/curves", response_model=List[CurveResponse])
def list_curves(well_id: int, db: Session = Depends(get_db)):
    curves = db.query(Curve).filter(Curve.well_id == well_id).all()

    if not curves:
        raise HTTPException(status_code=404, detail="No curves found for this well.")

    return curves


# Get Curve Data by Depth Range
@app.get("/api/curves/{curve_id}/data", response_model=List[MeasurementResponse])
def get_curve_data(
    curve_id: int,
    min_depth: float,
    max_depth: float,
    db: Session = Depends(get_db)
):
    if min_depth > max_depth:
        raise HTTPException(status_code=400, detail="min_depth cannot be greater than max_depth.")

    data = (
        db.query(Measurement)
        .filter(
            Measurement.curve_id == curve_id,
            Measurement.depth >= min_depth,
            Measurement.depth <= max_depth
        )
        .order_by(Measurement.depth.asc())
        .all()
    )

    if not data:
        raise HTTPException(status_code=404, detail="No data found for given range.")

    return data

# AI Interpretation
@app.post("/api/interpret")
def interpret(
    curve_id: int,
    min_depth: float,
    max_depth: float,
    db: Session = Depends(get_db)
):
    try:
        result = interpret_curve(db, curve_id, min_depth, max_depth)
        return result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
