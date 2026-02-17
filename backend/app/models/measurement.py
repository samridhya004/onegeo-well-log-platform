from sqlalchemy import Column, Integer, Float, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.db.base import Base


class Measurement(Base):
    __tablename__ = "measurements"

    id = Column(Integer, primary_key=True, index=True)
    curve_id = Column(Integer, ForeignKey("curves.id", ondelete="CASCADE"))
    depth = Column(Float, nullable=False)
    value = Column(Float, nullable=True)

    curve = relationship("Curve", backref="measurements")


Index("idx_curve_depth", Measurement.curve_id, Measurement.depth)
