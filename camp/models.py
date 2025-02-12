from sqlalchemy import ForeignKey, UniqueConstraint, create_engine, Column, DateTime, Enum, Integer, String, Boolean, func
from sqlalchemy.orm import DeclarativeBase, relationship
from django.contrib.auth.models import User

# Database engine
engine = create_engine("postgresql+psycopg2://postgres:ank@localhost:5432/temp")

# Base class
class Base(DeclarativeBase):
    pass

# Practice model
class Practice(Base):
    __tablename__ = 'practice'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey('userprofile.id'), nullable=False)
    
    # Back-populated relationship
    # userprofile = relationship("UserProfile", back_populates="practice")

# UserProfile model
class UserProfile(Base):
    __tablename__ = 'userprofile'
    id = Column(Integer,primary_key=True)
    practice_id = Column(Integer, ForeignKey('practice.id'))
    role = Column(Enum("superadmin", "admin", "practiceuser", name="role"), nullable=False)
    
    # Relationships
    # practice = relationship("Practice", back_populates="userprofile", uselist=False)
    # campaign = relationship("Campaign", back_populates="userprofile", uselist=False)

# Campaign model
class Campaign(Base):
    __tablename__ = 'campaign'
    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String(50), nullable=False)
    name = Column(String(50), nullable=False)
    description = Column(String, nullable=False)
    status = Column(Enum("upcoming", "running", "expired", name="status"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    # created_by = Column(Integer, ForeignKey('userprofile.id'), nullable=False)
    
    # Back-populated relationship
    # userprofile = relationship("UserProfile", back_populates="campaign")
    
class AdminCampaign(Base):
    __tablename__ = 'admincampaign'
    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String(50), nullable=False)
    name = Column(String(50), nullable=False)
    description = Column(String, nullable=False)
    status = Column(Enum("upcoming", "running", "expired", name="status"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    belongto = Column(Integer, ForeignKey('practice.id'))
    # created_by = Column(Integer, ForeignKey('userprofile.id'), nullable=False)
    
class Message(Base):
    __tablename__ = 'message'
    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String(50), nullable=False)
    name = Column(String(50), nullable=False)
    description = Column(String, nullable=False)
    status = Column(Enum("upcoming", "running", "expired", name="status"), nullable=False)
    userprofile_id = Column(Integer, ForeignKey('userprofile.id'), nullable=False)
    seen = Column(Enum("yes", "no", name="seen_status"), nullable=False, default="no")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
class UserCampaignSequence(Base):
    __tablename__ = 'usercampaignsequence'

    id = Column(Integer, primary_key=True, autoincrement=True)
    # sa_campaign_id = Column(Integer, ForeignKey('campaign.id'), nullable=True)
    # admin_campaign_id = Column(Integer, ForeignKey('admincampaign.id'), nullable=True)
    type = Column(String(50), nullable=False)
    name = Column(String(50), nullable=False)
    description = Column(String, nullable=False)
    status = Column(Enum("upcoming", "running", "expired", name="status"), nullable=False)
    scheduled_date = Column(DateTime(timezone=True), nullable=False)
    schedule_status = Column(String(50), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(Integer, nullable=False)
    userprofile_id = Column(Integer, ForeignKey('userprofile.id'), nullable=False)

    

# Create tables
Base.metadata.create_all(engine)
