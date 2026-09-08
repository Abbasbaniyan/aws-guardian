from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Boolean, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

class ActionAuditLog(Base):
    __tablename__ = "action_audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    instance_id = Column(String, index=True)
    instance_name = Column(String)
    action_type = Column(String)  # "STOP", "KEEP_RUNNING", "SNOOZE"
    initiated_by = Column(String, default="user")
    status = Column(String)  # "SUCCESS", "BLOCKED", "FAILED"
    reason = Column(String)
    is_protected_target = Column(Boolean, default=False)

# Local SQLite database for audit records
DATABASE_URL = "sqlite:///./guardian_audit.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)