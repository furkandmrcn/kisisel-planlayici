import customtkinter as ctk
from gui.styles import AppStyles
from datetime import datetime, timedelta
from models import DailyActivity, WeeklyPlan
from utils.streak_tracker import StreakTracker
from tkinter import messagebox

class Dashboard(ctk.CTkFrame):
    def __init__(self, master, db_manager):
        super().__init__(master, fg_color=AppStyles.COLORS['background'])
        self.db_manager = db_manager
        
        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        self._create_widgets()
        self.refresh_data()
    
    def _create_widgets(self):
        self.today_frame = AppStyles.create_card_frame(self)
        self.today_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        ctk.CTkLabel(
            self.today_frame,
            text="📅 Bugünün Özeti",
            font=AppStyles.get_font(18, "bold")
        ).pack(pady=10, padx=20, anchor="w")
        
        self.today_content = ctk.CTkFrame(self.today_frame, fg_color="transparent")
        self.today_content.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.streak_frame = AppStyles.create_card_frame(self)
        self.streak_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        ctk.CTkLabel(
            self.streak_frame,
            text="🔥 Streak Bilgileri",
            font=AppStyles.get_font(18, "bold")
        ).pack(pady=10, padx=20, anchor="w")
        
        self.streak_content = ctk.CTkFrame(self.streak_frame, fg_color="transparent")
        self.streak_content.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.progress_frame = AppStyles.create_card_frame(self)
        self.progress_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        ctk.CTkLabel(
            self.progress_frame,
            text="📊 Haftalık İlerleme",
            font=AppStyles.get_font(18, "bold")
        ).pack(pady=10, padx=20, anchor="w")
        
        self.progress_content = ctk.CTkFrame(self.progress_frame, fg_color="transparent")
        self.progress_content.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.quick_frame = AppStyles.create_card_frame(self)
        self.quick_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        
        ctk.CTkLabel(
            self.quick_frame,
            text="⚡ Hızlı Erişim",
            font=AppStyles.get_font(18, "bold")
        ).pack(pady=10, padx=20, anchor="w")
        
        actions = [
            ("📚 Kitap Okuma Kaydı", "activity"),
            ("💼 İş/Proje Ekle", "activity"),
            ("🎓 Eğitim Kaydı", "activity"),
            ("📝 Hızlı Not", "notes")
        ]
        
        for text, page in actions:
            btn = ctk.CTkButton(
                self.quick_frame,
                text=text,
                font=AppStyles.get_font(12),
                height=35,
                command=lambda p=page: self._navigate_to_page(p)
            )
            btn.pack(pady=5, padx=20, fill="x")
    
    def _navigate_to_page(self, page_name):
        main_window = self.winfo_toplevel()
        if hasattr(main_window, 'show_page'):
            main_window.show_page(page_name)
    
    def refresh_data(self):
        self._update_today_summary()
        self._update_streaks()
        self._update_weekly_progress()
        self.after(30000, self.refresh_data)
    
    def _update_today_summary(self):
        for widget in self.today_content.winfo_children():
            widget.destroy()
        
        session = self.db_manager.get_session()
        try:
            today = datetime.now().date()
            activities = session.query(DailyActivity).filter(
                DailyActivity.date == today
            ).all()
            
            if activities:
                total_duration = sum(a.duration_minutes or 0 for a in activities)
                completed = sum(1 for a in activities if a.status == 'Completed')
                
                ctk.CTkLabel(
                    self.today_content,
                    text=f"Toplam Aktivite: {len(activities)}",
                    font=AppStyles.get_font(14)
                ).pack(anchor="w", pady=5)
                
                ctk.CTkLabel(
                    self.today_content,
                    text=f"Tamamlanan: {completed}",
                    font=AppStyles.get_font(14)
                ).pack(anchor="w", pady=5)
                
                ctk.CTkLabel(
                    self.today_content,
                    text=f"Toplam Süre: {total_duration} dakika",
                    font=AppStyles.get_font(14)
                ).pack(anchor="w", pady=5)
                
                for activity in activities[:5]:
                    frame = ctk.CTkFrame(self.today_content, fg_color=AppStyles.COLORS['surface_hover'])
                    frame.pack(fill="x", pady=2)
                    
                    frame.configure(cursor="hand2")
                    
                    frame.bind("<Button-1>", lambda e, a=activity: self._show_activity_detail(a))
                    
                    ctk.CTkLabel(
                        frame,
                        text=f"{activity.category.icon} {activity.title}",
                        font=AppStyles.get_font(12)
                    ).pack(side="left", padx=5)
                    
                    for widget in frame.winfo_children():
                        widget.bind("<Button-1>", lambda e, a=activity: self._show_activity_detail(a))
                    
                    status_text = "✅" if activity.status == 'Completed' else "🔄"
                    ctk.CTkLabel(
                        frame,
                        text=status_text,
                        font=AppStyles.get_font(12)
                    ).pack(side="right", padx=5)
                    
                    delete_btn = ctk.CTkButton(
                        frame,
                        text="🗑",
                        width=25,
                        height=25,
                        fg_color="transparent",
                        hover_color=AppStyles.COLORS['error'],
                        command=lambda a=activity: self._delete_activity(a)
                    )
                    delete_btn.pack(side="right", padx=2)
            else:
                ctk.CTkLabel(
                    self.today_content,
                    text="Henüz aktivite kaydı yok",
                    font=AppStyles.get_font(14),
                    text_color=AppStyles.COLORS['text_secondary']
                ).pack(anchor="w", pady=20)
                
        finally:
            session.close()
    
    def _show_activity_detail(self, activity):
        session = self.db_manager.get_session()
        
        try:
            activity = session.merge(activity)
            
            dialog = ctk.CTkToplevel(self)
            dialog.title("Aktivite Detayı")
            dialog.geometry("550x500")
            dialog.grab_set()
            
            ctk.CTkLabel(
                dialog,
                text=f"{activity.category.icon} {activity.title}",
                font=AppStyles.get_font(18, "bold")
            ).pack(pady=10, padx=20, anchor="w")
            
            info_frame = ctk.CTkFrame(dialog, fg_color=AppStyles.COLORS['surface_hover'])
            info_frame.pack(fill="x", padx=20, pady=5)
            
            info_text = f"📅 Tarih: {activity.date.strftime('%d.%m.%Y')}\n"
            info_text += f"⏱️ Süre: {activity.duration_minutes or 0} dakika\n"
            info_text += f"📊 Öncelik: {activity.priority}\n"
            info_text += f"📌 Durum: {activity.status}"
            
            ctk.CTkLabel(
                info_frame,
                text=info_text,
                font=AppStyles.get_font(13),
                justify="left"
            ).pack(pady=10, padx=10, anchor="w")
            
            detail_frame = ctk.CTkFrame(dialog, fg_color=AppStyles.COLORS['surface_hover'])
            detail_frame.pack(fill="both", expand=True, padx=20, pady=10)
            
            detail_text = ""
            
            if activity.reading_detail:
                detail = activity.reading_detail
                detail_text = f"📚 Kitap Adı: {detail.book_name or 'Belirtilmemiş'}\n"
                detail_text += f"📖 Okunan Sayfa: {detail.pages_read or 0}\n"
                detail_text += f"{'─' * 40}\n"
                detail_text += f"📝 Alıntılar / Notlar:\n{detail.quotes or 'Yok'}"
            elif activity.work_detail:
                detail = activity.work_detail
                detail_text = f"💼 Proje Adı: {detail.project_title or 'Belirtilmemiş'}\n"
                detail_text += f"⏱️ Harcanan Süre: {detail.duration_hours or 0} saat\n"
                detail_text += f"{'─' * 40}\n"
                detail_text += f"✅ Tamamlanan Kısımlar:\n{detail.completed_tasks or 'Yok'}\n"
                detail_text += f"{'─' * 40}\n"
                detail_text += f"⏳ Eksik / Kalan Kısımlar:\n{detail.pending_tasks or 'Yok'}"
            elif activity.education_detail:
                detail = activity.education_detail
                detail_text = f"🎓 Kurs / Eğitim Adı: {detail.course_name or 'Belirtilmemiş'}\n"
                detail_text += f"⏱️ Harcanan Süre: {detail.duration_hours or 0} saat\n"
                detail_text += f"{'─' * 40}\n"
                detail_text += f"📚 Öğrenilen Konular / İçerik:\n{detail.topics_learned or 'Yok'}"
            elif activity.hobby_detail:
                detail = activity.hobby_detail
                detail_text = f"⚽ Aktivite Adı: {detail.activity_name or 'Belirtilmemiş'}\n"
                detail_text += f"⏱️ Süre: {detail.duration_minutes or 0} dakika\n"
                detail_text += f"{'─' * 40}\n"
                detail_text += f"📝 Açıklama:\n{detail.description or 'Yok'}"
            else:
                detail_text = activity.description or "Detay bilgisi yok"
            
            detail_box = ctk.CTkTextbox(
                detail_frame,
                font=AppStyles.get_font(13),
                wrap="word",
                height=200
            )
            detail_box.pack(fill="both", expand=True, padx=5, pady=5)
            detail_box.insert("1.0", detail_text)
            detail_box.configure(state="disabled")
            
            ctk.CTkButton(
                dialog,
                text="Kapat",
                font=AppStyles.get_font(13),
                height=35,
                command=dialog.destroy
            ).pack(pady=15, padx=20, fill="x")
            
        finally:
            session.close()
    
    def _delete_activity(self, activity):
        if messagebox.askyesno("Onay", f"'{activity.title}' aktivitesini silmek istiyor musunuz?"):
            session = self.db_manager.get_session()
            try:
                activity = session.merge(activity)
                
                if activity.reading_detail:
                    session.delete(activity.reading_detail)
                if activity.work_detail:
                    session.delete(activity.work_detail)
                if activity.education_detail:
                    session.delete(activity.education_detail)
                if activity.hobby_detail:
                    session.delete(activity.hobby_detail)
                
                session.delete(activity)
                session.commit()
                
                tracker = StreakTracker(self.db_manager)
                tracker.recalculate_all_streaks()
                
                self._update_today_summary()
                self._update_streaks()
                
            except Exception as e:
                session.rollback()
                messagebox.showerror("Hata", f"Silme işlemi başarısız:\n{str(e)}")
            finally:
                session.close()
    
    def _update_streaks(self):
        for widget in self.streak_content.winfo_children():
            widget.destroy()
        
        tracker = StreakTracker(self.db_manager)
        streaks = tracker.get_streaks_summary()
        
        for streak in streaks:
            frame = ctk.CTkFrame(self.streak_content, fg_color=AppStyles.COLORS['surface_hover'])
            frame.pack(fill="x", pady=5, padx=5)
            
            ctk.CTkLabel(
                frame,
                text=f"{streak['category_icon']} {streak['category_name']}",
                font=AppStyles.get_font(13, "bold")
            ).pack(side="left", padx=10, pady=5)
            
            streak_frame = ctk.CTkFrame(frame, fg_color="transparent")
            streak_frame.pack(side="right", padx=10)
            
            ctk.CTkLabel(
                streak_frame,
                text=f"🔥 {streak['current_streak']}",
                font=AppStyles.get_font(18, "bold"),
                text_color="#FF9800"
            ).pack(side="left")
            
            ctk.CTkLabel(
                streak_frame,
                text=" gün",
                font=AppStyles.get_font(12),
                text_color=AppStyles.COLORS['text_secondary']
            ).pack(side="left")
    
    def _update_weekly_progress(self):
        for widget in self.progress_content.winfo_children():
            widget.destroy()
        
        session = self.db_manager.get_session()
        try:
            today = datetime.now().date()
            week_start = today - timedelta(days=today.weekday())
            
            total_plans = session.query(WeeklyPlan).filter(
                WeeklyPlan.week_start_date == week_start
            ).count()
            
            completed_plans = session.query(WeeklyPlan).filter(
                WeeklyPlan.week_start_date == week_start,
                WeeklyPlan.is_completed == True
            ).count()
            
            if total_plans > 0:
                completion_rate = (completed_plans / total_plans) * 100
                
                ctk.CTkLabel(
                    self.progress_content,
                    text=f"Bu Hafta: {completed_plans}/{total_plans} görev tamamlandı",
                    font=AppStyles.get_font(14, "bold")
                ).pack(pady=10)
                
                progress = ctk.CTkProgressBar(self.progress_content)
                progress.pack(pady=10, padx=20, fill="x")
                progress.set(completion_rate / 100)
                
                ctk.CTkLabel(
                    self.progress_content,
                    text=f"%{completion_rate:.1f}",
                    font=AppStyles.get_font(24, "bold"),
                    text_color="#4CAF50"
                ).pack()
            else:
                ctk.CTkLabel(
                    self.progress_content,
                    text="Bu hafta için henüz plan yok",
                    font=AppStyles.get_font(14),
                    text_color=AppStyles.COLORS['text_secondary']
                ).pack(pady=20)
                
        finally:
            session.close()