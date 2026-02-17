from pydantic import BaseModel


class MeasurementResponse(BaseModel):
    depth: float
    value: float | None

    class Config:
        from_attributes = True
