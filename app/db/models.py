from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base


class Attack(Base):
    __tablename__ = "attacks"

    id          = Column(Integer, primary_key=True, index=True)
    name        = Column(String(150), nullable=False)
    attack_type = Column(String(20), nullable=False)
    target      = Column(String(255), nullable=False)
    scope       = Column(Text, nullable=True)
    objective   = Column(Text, nullable=True)
    status      = Column(String(50), nullable=False, default="Queued")
    response    = Column(Text, nullable=True)
    ai_analysis = Column(Text, nullable=True)
    created_at  = Column(DateTime, server_default=func.now())

    scans = relationship("Scan", back_populates="attack", cascade="all, delete")


class Scan(Base):
    __tablename__ = "scans"

    id                   = Column(Integer, primary_key=True, index=True)
    attack_id            = Column(Integer, ForeignKey("attacks.id"), nullable=False)
    tool                 = Column(String(100), nullable=False)
    command              = Column(Text, nullable=True)
    raw_output           = Column(Text, nullable=True)
    ai_analysis          = Column(Text, nullable=True)
    vulnerabilities_found = Column(Text, nullable=True)
    next_action          = Column(Text, nullable=True)
    status               = Column(String(50), default="Queued")
    created_at           = Column(DateTime, server_default=func.now())

    attack = relationship("Attack", back_populates="scans")