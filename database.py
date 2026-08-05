from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from models import Base, Category, Streak
from datetime import datetime
import os
import shutil
import json
import csv

class DatabaseManager:
    def __init__(self, db_path='planner.db'):
        self.db_path = db_path
        self.engine = create_engine(f'sqlite:///{db_path}', echo=False)
        self.Session = scoped_session(sessionmaker(bind=self.engine))
        
        Base.metadata.create_all(self.engine)
        self._initialize_default_categories()
    
    def _initialize_default_categories(self):
        session = self.Session()
        
        default_categories = [
            {'name': 'Kitap / Okuma', 'icon': '📚', 'color': '#4CAF50'},
            {'name': 'İş / Proje', 'icon': '💼', 'color': '#2196F3'},
            {'name': 'Eğitim', 'icon': '🎓', 'color': '#9C27B0'},
            {'name': 'Hobi / Spor', 'icon': '⚽', 'color': '#FF9800'},
            {'name': 'Kişisel', 'icon': '👤', 'color': '#607D8B'},
            {'name': 'Diğer', 'icon': '📌', 'color': '#795548'},
        ]
        
        for cat_data in default_categories:
            existing = session.query(Category).filter_by(name=cat_data['name']).first()
            if not existing:
                category = Category(**cat_data)
                session.add(category)
                streak = Streak(category=category)
                session.add(streak)
        
        session.commit()
        session.close()
    
    def get_session(self):
        return self.Session()
    
    def backup_database(self, backup_path=None):
        if backup_path is None:
            backup_dir = 'backups'
            os.makedirs(backup_dir, exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = os.path.join(backup_dir, f'planner_backup_{timestamp}.db')
        
        shutil.copy2(self.db_path, backup_path)
        return backup_path
    
    def export_to_json(self, filepath):
        session = self.Session()
        data = {'activities': [], 'plans': [], 'notes': []}
        
        activities = session.query(self._get_activity_model()).all()
        for a in activities:
            data['activities'].append({
                'id': a.id,
                'date': str(a.date),
                'category': a.category.name,
                'title': a.title,
                'duration_minutes': a.duration_minutes,
                'priority': a.priority,
                'status': a.status
            })
        
        plans = session.query(self._get_plan_model()).all()
        for p in plans:
            data['plans'].append({
                'id': p.id,
                'week_start_date': str(p.week_start_date),
                'day_of_week': p.day_of_week,
                'title': p.title,
                'is_completed': p.is_completed
            })
        
        notes = session.query(self._get_note_model()).all()
        for n in notes:
            data['notes'].append({
                'id': n.id,
                'title': n.title,
                'content': n.content
            })
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        session.close()
    
    def _get_activity_model(self):
        from models import DailyActivity
        return DailyActivity
    
    def _get_plan_model(self):
        from models import WeeklyPlan
        return WeeklyPlan
    
    def _get_note_model(self):
        from models import Note
        return Note