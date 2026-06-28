"""
SQLAlchemy model for storing incidents in SQLite database.
"""
import datetime
from sqlalchemy import Column, String, Float, DateTime, Text
from sqlalchemy.sql import func
from backend.app.database import Base


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(String, primary_key=True, index=True)
    service = Column(String, nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    cpu_usage = Column(Float, default=0.0)
    memory_usage = Column(Float, default=0.0)
    latency_ms = Column(Float, default=0.0)
    error_rate = Column(Float, default=0.0)
    anomaly_score = Column(Float, default=0.0)
    root_cause = Column(Text, nullable=True)
    technical_explanation = Column(Text, nullable=True)
    responsible_file = Column(String, nullable=True)
    suspected_commit = Column(String, nullable=True)
    fix_patch = Column(Text, nullable=True)
    fix_explanation = Column(Text, nullable=True)
    risk_level = Column(String, default="MEDIUM")
    testing_suggestions = Column(Text, nullable=True)  # JSON-encoded array
    post_mortem = Column(Text, nullable=True)
    status = Column(String, default="open")  # "open", "resolved"
    pipeline_status = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())


# Alias so both IncidentRecord and Incident can be used interchangeably
IncidentRecord = Incident
