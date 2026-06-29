import enum
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, Boolean, ForeignKey, JSON

db = SQLAlchemy()

class PostStatus(enum.Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    FAILED = "failed"

class ConnectionJobStatus(enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class LogLevel(enum.Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"

class Config(db.Model):
    __tablename__ = 'configurations'
    
    id = Column(Integer, primary_key=True)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class LinkedInCredential(db.Model):
    __tablename__ = 'linkedin_credentials'
    
    id = Column(Integer, primary_key=True)
    access_token = Column(Text, nullable=False)
    refresh_token = Column(Text, nullable=True)
    token_expires_at = Column(DateTime, nullable=False)
    refresh_token_expires_at = Column(DateTime, nullable=True)
    linkedin_user_id = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Post(db.Model):
    __tablename__ = 'posts'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    status = Column(Enum(PostStatus), default=PostStatus.DRAFT, nullable=False)
    scheduled_at = Column(DateTime, nullable=True)
    published_at = Column(DateTime, nullable=True)
    linkedin_post_id = Column(String(255), nullable=True)
    retry_count = Column(Integer, default=0)
    last_error = Column(Text, nullable=True)
    job_id = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Log(db.Model):
    __tablename__ = 'logs'
    
    id = Column(Integer, primary_key=True)
    level = Column(Enum(LogLevel), default=LogLevel.INFO, nullable=False)
    message = Column(Text, nullable=False)
    context = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class ConnectionConfiguration(db.Model):
    __tablename__ = 'connection_configurations'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    
    # Search filters
    company = Column(String(255), nullable=True)
    role = Column(String(255), nullable=True)
    industry = Column(String(255), nullable=True)
    location = Column(String(255), nullable=True)
    university = Column(String(255), nullable=True)
    keywords = Column(Text, nullable=True)
    
    # Limits and cooldown
    daily_limit = Column(Integer, default=20)
    request_cooldown = Column(Integer, default=5)  # Seconds
    connection_message = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class LinkedInProfile(db.Model):
    __tablename__ = 'linkedin_profiles'
    
    id = Column(Integer, primary_key=True)
    profile_url = Column(String(500), unique=True, nullable=False)
    profile_id = Column(String(255), nullable=True)
    name = Column(String(255), nullable=True)
    title = Column(String(500), nullable=True)
    company = Column(String(255), nullable=True)
    location = Column(String(255), nullable=True)
    industry = Column(String(255), nullable=True)
    university = Column(String(255), nullable=True)
    headline = Column(Text, nullable=True)
    about = Column(Text, nullable=True)
    
    # Connection status
    is_connected = Column(Boolean, default=False)
    connection_request_sent = Column(Boolean, default=False)
    connection_request_sent_at = Column(DateTime, nullable=True)
    connection_accepted = Column(Boolean, default=False)
    connection_accepted_at = Column(DateTime, nullable=True)
    
    # Job association
    job_id = Column(Integer, ForeignKey('connection_jobs.id'), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ConnectionJob(db.Model):
    __tablename__ = 'connection_jobs'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    status = Column(Enum(ConnectionJobStatus), default=ConnectionJobStatus.PENDING, nullable=False)
    configuration_id = Column(Integer, ForeignKey('connection_configurations.id'), nullable=True)
    
    target_count = Column(Integer, nullable=True)
    completed_count = Column(Integer, default=0)
    failed_count = Column(Integer, default=0)
    skipped_count = Column(Integer, default=0)
    
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    last_run_at = Column(DateTime, nullable=True)
    
    error_message = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class DailyConnectionStats(db.Model):
    __tablename__ = 'daily_connection_stats'
    
    id = Column(Integer, primary_key=True)
    date = Column(String(10), nullable=False, unique=True)  # YYYY-MM-DD
    requests_sent = Column(Integer, default=0)
    requests_accepted = Column(Integer, default=0)
    requests_failed = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
