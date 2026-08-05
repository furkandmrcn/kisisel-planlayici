from datetime import datetime, timedelta
from models import DailyActivity, Streak


class StreakTracker:
    def __init__(self, db_manager):
        self.db_manager = db_manager
    
    def update_streak(self, category_id):
        session = self.db_manager.get_session()
        
        try:
            streak = session.query(Streak).filter_by(category_id=category_id).first()
            
            if streak:
                today = datetime.now().date()
                yesterday = today - timedelta(days=1)
                
                if streak.last_activity_date == yesterday:
                    streak.current_streak += 1
                elif streak.last_activity_date != today:
                    streak.current_streak = 1
                
                if streak.current_streak > streak.longest_streak:
                    streak.longest_streak = streak.current_streak
                
                streak.last_activity_date = today
                session.commit()
            
            return streak.current_streak if streak else 0
            
        finally:
            session.close()
    
    def get_streaks_summary(self):
        session = self.db_manager.get_session()
        
        try:
            streaks = session.query(Streak).all()
            summary = []
            
            for streak in streaks:
                summary.append({
                    'category_name': streak.category.name,
                    'category_icon': streak.category.icon,
                    'category_color': streak.category.color,
                    'current_streak': streak.current_streak,
                    'longest_streak': streak.longest_streak
                })
            
            return summary
            
        finally:
            session.close()

    def reset_streak(self, category_id):
        """Belirli bir kategorinin streak'ini sıfırla"""
        session = self.db_manager.get_session()
    
        try:
            streak = session.query(Streak).filter_by(category_id=category_id).first()
        
            if streak:
                streak.current_streak = 0
                streak.last_activity_date = None
                session.commit()
            
        finally:
            session.close()

    def recalculate_all_streaks(self):
        """Tüm streak'leri yeniden hesapla"""
        session = self.db_manager.get_session()
    
        try:
            from models import Category
        
            categories = session.query(Category).all()
        
            for category in categories:
                # Son aktivite tarihini bul
                last_activity = session.query(DailyActivity).filter(
                DailyActivity.category_id == category.id
                ).order_by(DailyActivity.date.desc()).first()
            
                streak = session.query(Streak).filter_by(category_id=category.id).first()
            
                if last_activity:
                    # Son aktivite bugün veya dün mü kontrol et
                    today = datetime.now().date()
                    last_date = last_activity.date
                
                    if last_date == today:
                        # Bugün aktivite var, streak'i kontrol et
                        consecutive = 1
                        check_date = today - timedelta(days=1)
                    
                        while True:
                            activity = session.query(DailyActivity).filter(
                            DailyActivity.category_id == category.id,
                            DailyActivity.date == check_date
                            ).first()
                        
                            if activity:
                                consecutive += 1
                                check_date -= timedelta(days=1)
                            else:
                                break
                    
                        streak.current_streak = consecutive
                        streak.last_activity_date = today
                    
                        if consecutive > streak.longest_streak:
                            streak.longest_streak = consecutive
                        
                    elif last_date == today - timedelta(days=1):
                        # Dün aktivite var
                        streak.current_streak = 1
                        streak.last_activity_date = last_date
                    else:
                        # Daha eski, streak kırılmış
                        streak.current_streak = 0
                        streak.last_activity_date = last_date
                else:
                    # Hiç aktivite yok
                    streak.current_streak = 0
                    streak.last_activity_date = None
                    streak.longest_streak = 0
        
            session.commit()
        
        finally:
            session.close()