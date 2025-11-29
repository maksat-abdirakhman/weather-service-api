from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text
from app.database import Base


class ActionLog(Base):
    """Model for storing action logs."""
    
    __tablename__ = "action_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Action details
    action = Column(String(50), nullable=False, index=True)  # CREATE, UPDATE, DELETE, FETCH
    entity = Column(String(50), nullable=False)  # weather, city, etc.
    entity_id = Column(Integer, nullable=True)  # ID of affected entity
    
    # Details
    details = Column(Text, nullable=True)  # JSON or text with additional info
    status = Column(String(20), nullable=False, default="success")  # success, error
    error_message = Column(Text, nullable=True)
    
    # Metadata
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    def __repr__(self):
        return f"<ActionLog(action={self.action}, entity={self.entity}, status={self.status})>"

