from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from app.db.database import Base


class Attack(Base):
    __tablename__ = "attacks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    attack_type = Column(String(20), nullable=False)
    target = Column(String(255), nullable=False)
    scope = Column(Text, nullable=True)
    objective = Column(Text, nullable=True)
    status = Column(String(50), nullable=False, default="Queued")
    created_at = Column(DateTime, server_default=func.now())