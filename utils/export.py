import json
import csv
from models import DailyActivity, WeeklyPlan, Note

class DataExporter:
    def __init__(self, db_manager):
        self.db_manager = db_manager
    
    def export_to_json(self, filepath):
        session = self.db_manager.get_session()
        data = {'activities': [], 'plans': [], 'notes': []}
        
        activities = session.query(DailyActivity).all()
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
        
        plans = session.query(WeeklyPlan).all()
        for p in plans:
            data['plans'].append({
                'id': p.id,
                'week_start_date': str(p.week_start_date),
                'day_of_week': p.day_of_week,
                'title': p.title,
                'is_completed': p.is_completed
            })
        
        notes = session.query(Note).all()
        for n in notes:
            data['notes'].append({
                'id': n.id,
                'title': n.title,
                'content': n.content
            })
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        session.close()
        return filepath
    
    def export_to_csv(self, filepath):
        session = self.db_manager.get_session()
        activities = session.query(DailyActivity).all()
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['ID', 'Tarih', 'Kategori', 'Başlık', 'Süre(dk)', 'Öncelik', 'Durum'])
            
            for a in activities:
                writer.writerow([
                    a.id, a.date, a.category.name, a.title,
                    a.duration_minutes, a.priority, a.status
                ])
        
        session.close()
        return filepath