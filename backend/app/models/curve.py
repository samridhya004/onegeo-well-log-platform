from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base


class Curve(Base):
    __tablename__ = "curves"

    id = Column(Integer, primary_key=True, index=True)
    well_id = Column(Integer, ForeignKey("wells.id", ondelete="CASCADE"))
    mnemonic = Column(String, nullable=False)
    unit = Column(String, nullable=True)
    description = Column(String, nullable=True)

    well = relationship("Well", backref="curves")
