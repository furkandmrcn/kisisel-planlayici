import customtkinter as ctk
from gui.styles import AppStyles
from models import DailyActivity
from datetime import datetime, timedelta
from tkinter import messagebox
from utils.streak_tracker import StreakTracker

class HistoryPage(ctk.CTkFrame):
    def __init__(self, master, db_manager):
        super().__init__(master, fg_color=AppStyles.COLORS['background'])
        self.db_manager = db_manager
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        
        self._create_widgets()
        self.refresh_data()
    
    def _create_widgets(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=10)
        
        ctk.CTkLabel(
            header,
            text="📋 Geçmiş Aktiviteler",
            font=AppStyles.get_font(24, "bold")
        ).pack(side="left")
        
        filter_frame = ctk.CTkFrame(header, fg_color="transparent")
        filter_frame.pack(side="right")
        
        ctk.CTkLabel(filter_frame, text="Filtre:", font=AppStyles.get_font(12)).pack(side="left", padx=5)
        
        self.filter_var = ctk.StringVar(value="Tümü")
        filter_menu = ctk.CTkOptionMenu(
            filter_frame,
            values=["Tümü", "Bugün", "Bu Hafta", "Bu Ay", "Kitap / Okuma", "İş / Proje", "Eğitim", "Hobi / Spor"],
            variable=self.filter_var,
            command=self._on_filter_change,
            font=AppStyles.get_font(12),
            width=130
        )
        filter_menu.pack(side="left", padx=5)
        
        self.history_frame = ctk.CTkScrollableFrame(
            self,
            fg_color=AppStyles.COLORS['surface']
        )
        self.history_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
    
    def _on_filter_change(self, value):
        self.refresh_data()
    
    def refresh_data(self):
        for widget in self.history_frame.winfo_children():
            widget.destroy()
        
        session = self.db_manager.get_session()
        try:
            filter_value = self.filter_var.get()
            query = session.query(DailyActivity).order_by(DailyActivity.date.desc())
            
            today = datetime.now().date()
            
            if filter_value == "Bugün":
                query = query.filter(DailyActivity.date == today)
            elif filter_value == "Bu Hafta":
                week_start = today - timedelta(days=today.weekday())
                query = query.filter(DailyActivity.date >= week_start)
            elif filter_value == "Bu Ay":
                month_start = today.replace(day=1)
                query = query.filter(DailyActivity.date >= month_start)
            elif filter_value in ["Kitap / Okuma", "İş / Proje", "Eğitim", "Hobi / Spor"]:
                query = query.join(DailyActivity.category).filter_by(name=filter_value)
            
            activities = query.limit(50).all()
            
            if not activities:
                ctk.CTkLabel(
                    self.history_frame,
                    text="Gösterilecek aktivite yok",
                    font=AppStyles.get_font(14),
                    text_color=AppStyles.COLORS['text_secondary']
                ).pack(pady=30)
            else:
                for activity in activities:
                    self._create_activity_card(activity)
                    
        finally:
            session.close()
    
    def _create_activity_card(self, activity):
        card = AppStyles.create_card_frame(
            self.history_frame,
            fg_color=AppStyles.COLORS['surface_hover']
        )
        card.pack(fill="x", pady=3, padx=5)
        
        top_row = ctk.CTkFrame(card, fg_color="transparent")
        top_row.pack(fill="x", padx=10, pady=(10, 5))
        
        ctk.CTkLabel(
            top_row,
            text=f"{activity.category.icon} {activity.title}",
            font=AppStyles.get_font(14, "bold")
        ).pack(side="left")
        
        status_text = "✅ Tamamlandı" if activity.status == 'Completed' else "🔄 Devam Ediyor"
        status_color = AppStyles.COLORS['success'] if activity.status == 'Completed' else AppStyles.COLORS['warning']
        ctk.CTkLabel(
            top_row,
            text=status_text,
            font=AppStyles.get_font(11),
            text_color=status_color
        ).pack(side="right")
        
        detail_row = ctk.CTkFrame(card, fg_color="transparent")
        detail_row.pack(fill="x", padx=10, pady=(0, 5))
        
        info_text = f"📅 {activity.date.strftime('%d.%m.%Y')}  |  ⏱️ {activity.duration_minutes or 0} dk  |  📊 {activity.priority}"
        ctk.CTkLabel(
            detail_row,
            text=info_text,
            font=AppStyles.get_font(11),
            text_color=AppStyles.COLORS['text_secondary']
        ).pack(side="left")
        
        btn_row = ctk.CTkFrame(card, fg_color="transparent")
        btn_row.pack(fill="x", padx=10, pady=(0, 10))
        
        ctk.CTkButton(
            btn_row,
            text="🔍 Detay",
            font=AppStyles.get_font(11),
            width=60,
            height=25,
            command=lambda a=activity: self._show_activity_detail(a)
        ).pack(side="left", padx=2)
        
        ctk.CTkButton(
            btn_row,
            text="🗑 Sil",
            font=AppStyles.get_font(11),
            width=50,
            height=25,
            fg_color=AppStyles.COLORS['error'],
            hover_color="#d32f2f",
            command=lambda a=activity: self._delete_activity(a)
        ).pack(side="right", padx=2)
    
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
        if messagebox.askyesno("Onay", f"'{activity.title}' aktivitesini silmek istiyor musunuz?\nBu işlem geri alınamaz!"):
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
                
                self.refresh_data()
                
            except Exception as e:
                session.rollback()
                messagebox.showerror("Hata", f"Silme işlemi başarısız:\n{str(e)}")
            finally:
                session.close()