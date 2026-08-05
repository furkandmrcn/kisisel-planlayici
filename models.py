from sqlalchemy import create_engine, Column, Integer, String, Float, Date, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Category(Base):
    __tablename__ = 'categories'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    icon = Column(String(50))
    color = Column(String(20))
    created_at = Column(DateTime, default=datetime.now)
    
    daily_activities = relationship("DailyActivity", back_populates="category")
    weekly_plans = relationship("WeeklyPlan", back_populates="category")
    notes = relationship("Note", back_populates="category")
    streaks = relationship("Streak", back_populates="category")

class DailyActivity(Base):
    __tablename__ = 'daily_activities'
    
    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    duration_minutes = Column(Integer)
    priority = Column(String(20), default='Medium')
    status = Column(String(20), default='In Progress')
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    category = relationship("Category", back_populates="daily_activities")
    reading_detail = relationship("ReadingDetail", uselist=False, back_populates="activity")
    work_detail = relationship("WorkDetail", uselist=False, back_populates="activity")
    education_detail = relationship("EducationDetail", uselist=False, back_populates="activity")
    hobby_detail = relationship("HobbyDetail", uselist=False, back_populates="activity")

class ReadingDetail(Base):
    __tablename__ = 'reading_details'
    
    id = Column(Integer, primary_key=True)
    activity_id = Column(Integer, ForeignKey('daily_activities.id'), unique=True)
    book_name = Column(String(200))
    pages_read = Column(Integer)
    quotes = Column(Text)
    notes = Column(Text)
    
    activity = relationship("DailyActivity", back_populates="reading_detail")

class WorkDetail(Base):
    __tablename__ = 'work_details'
    
    id = Column(Integer, primary_key=True)
    activity_id = Column(Integer, ForeignKey('daily_activities.id'), unique=True)
    project_title = Column(String(200))
    completed_tasks = Column(Text)
    pending_tasks = Column(Text)
    duration_hours = Column(Float)
    
    activity = relationship("DailyActivity", back_populates="work_detail")

class EducationDetail(Base):
    __tablename__ = 'education_details'
    
    id = Column(Integer, primary_key=True)
    activity_id = Column(Integer, ForeignKey('daily_activities.id'), unique=True)
    course_name = Column(String(200))
    topics_learned = Column(Text)
    duration_hours = Column(Float)
    
    activity = relationship("DailyActivity", back_populates="education_detail")

class HobbyDetail(Base):
    __tablename__ = 'hobby_details'
    
    id = Column(Integer, primary_key=True)
    activity_id = Column(Integer, ForeignKey('daily_activities.id'), unique=True)
    activity_name = Column(String(200))
    description = Column(Text)
    duration_minutes = Column(Integer)
    
    activity = relationship("DailyActivity", back_populates="hobby_detail")

class WeeklyPlan(Base):
    __tablename__ = 'weekly_plans'
    
    id = Column(Integer, primary_key=True)
    week_start_date = Column(Date, nullable=False)
    day_of_week = Column(Integer, nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    category_id = Column(Integer, ForeignKey('categories.id'))
    priority = Column(String(20), default='Medium')
    is_completed = Column(Boolean, default=False)
    activity_id = Column(Integer, ForeignKey('daily_activities.id'))
    created_at = Column(DateTime, default=datetime.now)
    
    category = relationship("Category", back_populates="weekly_plans")

class Note(Base):
    __tablename__ = 'notes'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    content = Column(Text)
    category_id = Column(Integer, ForeignKey('categories.id'))
    is_transferred = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    category = relationship("Category", back_populates="notes")

class Streak(Base):
    __tablename__ = 'streaks'
    
    id = Column(Integer, primary_key=True)
    category_id = Column(Integer, ForeignKey('categories.id'), unique=True)
    current_streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    last_activity_date = Column(Date)
    
    category = relationship("Category", back_populates="streaks")