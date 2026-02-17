from sqlalchemy.orm import Session
from app.models.curve import Curve
from app.models.measurement import Measurement
import statistics


def interpret_curve(db: Session, curve_id: int, min_depth: float, max_depth: float):
    """
    Layered interpretation pipeline:

    1. Data extraction & validation
    2. Statistical analysis (generic, applies to all curves)
    3. Domain-aware rule enhancement (optional based on mnemonic)
    """

    # 1. Data Extraction Layer

    curve = db.query(Curve).filter(Curve.id == curve_id).first()
    if not curve:
        raise ValueError("Curve not found.")

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
        raise ValueError("No data found in selected depth range.")

    values = [m.value for m in data if m.value is not None]

    if not values:
        raise ValueError("No valid measurement values.")

    # 2.Statistical Analysis Layer

    min_val = min(values)
    max_val = max(values)
    avg_val = statistics.mean(values)
    std_val = statistics.pstdev(values)

    interpretation = []

    # Variability classification
    if std_val < 5:
        interpretation.append("Low variability suggests stable formation properties.")
    elif std_val > 20:
        interpretation.append("High variability indicates significant property changes across interval.")
    else:
        interpretation.append("Moderate variability observed in selected interval.")

    # Trend detection
    first_val = values[0]
    last_val = values[-1]

    if last_val > first_val * 1.1:
        interpretation.append("Increasing trend detected across selected depth range.")
    elif last_val < first_val * 0.9:
        interpretation.append("Decreasing trend detected across selected depth range.")
    else:
        interpretation.append("No strong directional trend observed in selected interval.")

    # Range spread insight
    spread = max_val - min_val
    if spread > avg_val * 0.5:
        interpretation.append("Wide value spread suggests heterogeneous formation characteristics.")

    # 3. Domain-Aware Rule Layer

    mnemonic = curve.mnemonic.upper()

    # Gamma Ray
    if "GR" in mnemonic:
        if avg_val > 75:
            interpretation.append("Gamma ray levels suggest shale-rich lithology.")
        elif avg_val < 50:
            interpretation.append("Lower gamma ray values may indicate cleaner sand intervals.")

    # Resistivity
    if "RT" in mnemonic or "RES" in mnemonic:
        if avg_val > 20:
            interpretation.append("Elevated resistivity may indicate hydrocarbon potential.")
        elif avg_val < 5:
            interpretation.append("Low resistivity suggests water-bearing or conductive formation.")

    # Bulk Density
    if "RHOB" in mnemonic:
        if avg_val < 2.3:
            interpretation.append("Lower density may indicate porous formation.")
        elif avg_val > 2.65:
            interpretation.append("Higher density suggests tighter rock matrix.")

    # Sonic
    if "DT" in mnemonic:
        if avg_val > 100:
            interpretation.append("High sonic travel time may indicate softer or more porous intervals.")

    # Final Structured Output

    return {
        "curve": mnemonic,
        "statistics": {
            "min": round(min_val, 2),
            "max": round(max_val, 2),
            "average": round(avg_val, 2),
            "std_dev": round(std_val, 2),
            "count": len(values)
        },
        "interpretation": interpretation
    }
