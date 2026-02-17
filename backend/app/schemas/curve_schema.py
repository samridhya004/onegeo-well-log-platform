from pydantic import BaseModel


class CurveResponse(BaseModel):
    id: int
    mnemonic: str
    unit: str | None
    description: str | None

    class Config:
        from_attributes = True
