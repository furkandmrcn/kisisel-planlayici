import customtkinter as ctk
from gui.styles import AppStyles
from models import DailyActivity, ReadingDetail
from sqlalchemy import func
from datetime import datetime, timedelta
from tkinter import messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class AnalyticsPage(ctk.CTkFrame):
    def __init__(self, master, db_manager):
        super().__init__(master, fg_color=AppStyles.COLORS['background'])
        self.db_manager = db_manager
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        
        self._create_widgets()
        self.refresh_analytics()
    
    def _create_widgets(self):
        # Başlık ve butonlar
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=10)
        
        ctk.CTkLabel(header, text="📈 Analiz ve İstatistikler", font=AppStyles.get_font(24, "bold")).pack(side="left")
        
        export_frame = ctk.CTkFrame(header, fg_color="transparent")
        export_frame.pack(side="right")
        
        ctk.CTkButton(
            export_frame,
            text="JSON Export",
            font=AppStyles.get_font(11),
            width=100,
            command=lambda: self._export_data('json')
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            export_frame,
            text="CSV Export",
            font=AppStyles.get_font(11),
            width=100,
            command=lambda: self._export_data('csv')
        ).pack(side="left", padx=5)
        
        # İstatistik kartları
        self.stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.stats_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        
        self.stats_frame.grid_columnconfigure(0, weight=1)
        self.stats_frame.grid_columnconfigure(1, weight=1)
        self.stats_frame.grid_rowconfigure(0, weight=1)
        self.stats_frame.grid_rowconfigure(1, weight=1)
        
        self.stat_cards = {}
        card_data = [
            ("toplam_aktivite", "Toplam Aktivite", "0"),
            ("toplam_sure", "Toplam Süre", "0 dk"),
            ("okunan_sayfa", "Okunan Sayfa", "0"),
            ("tamamlanan", "Tamamlanan İş", "0")
        ]
        
        for i, (key, title, value) in enumerate(card_data):
            card = AppStyles.create_card_frame(self.stats_frame)
            card.grid(row=i//2, column=i%2, padx=5, pady=5, sticky="nsew")
            
            ctk.CTkLabel(card, text=title, font=AppStyles.get_font(13), text_color=AppStyles.COLORS['text_secondary']).pack(pady=(10, 5))
            
            value_label = ctk.CTkLabel(card, text=value, font=AppStyles.get_font(28, "bold"))
            value_label.pack(pady=(0, 10))
            
            self.stat_cards[key] = value_label
        
        # Grafik alanı
        self.chart_frame = AppStyles.create_card_frame(self.stats_frame)
        self.chart_frame.grid(row=0, column=2, rowspan=2, padx=5, pady=5, sticky="nsew")
        self.stats_frame.grid_columnconfigure(2, weight=2)
        
        ctk.CTkLabel(self.chart_frame, text="Haftalık Aktivite Grafiği", font=AppStyles.get_font(14, "bold")).pack(pady=10)
        
        self.chart_content = ctk.CTkFrame(self.chart_frame, fg_color="transparent")
        self.chart_content.pack(fill="both", expand=True, padx=10, pady=10)
    
    def refresh_analytics(self):
        session = self.db_manager.get_session()
        
        try:
            # Toplam aktivite
            total_activities = session.query(DailyActivity).count()
            self.stat_cards['toplam_aktivite'].configure(text=str(total_activities))
            
            # Toplam süre (saat:dakika formatında)
            total_duration = session.query(func.sum(DailyActivity.duration_minutes)).scalar() or 0
            hours = total_duration // 60
            minutes = total_duration % 60
            if hours > 0:
                self.stat_cards['toplam_sure'].configure(text=f"{hours}s {minutes}dk")
            else:
                self.stat_cards['toplam_sure'].configure(text=f"{minutes} dk")
            
            # Okunan sayfa
            total_pages = session.query(func.sum(ReadingDetail.pages_read)).scalar() or 0
            self.stat_cards['okunan_sayfa'].configure(text=str(total_pages))
            
            # Tamamlanan iş
            completed = session.query(DailyActivity).filter(DailyActivity.status == 'Completed').count()
            self.stat_cards['tamamlanan'].configure(text=str(completed))
            
            # Grafiği güncelle
            self._update_chart(session)
            
        finally:
            session.close()
    
    def _update_chart(self, session):
        for widget in self.chart_content.winfo_children():
            widget.destroy()
        
        today = datetime.now().date()
        week_ago = today - timedelta(days=6)
        
        daily_data = session.query(
            DailyActivity.date,
            func.sum(DailyActivity.duration_minutes)
        ).filter(
            DailyActivity.date >= week_ago,
            DailyActivity.date <= today
        ).group_by(DailyActivity.date).all()
        
        dates = []
        durations = []
        
        for i in range(7):
            date = week_ago + timedelta(days=i)
            dates.append(date.strftime("%d.%m"))
            
            duration = next((d[1] for d in daily_data if d[0] == date), 0)
            durations.append(duration or 0)
        
        fig, ax = plt.subplots(figsize=(5, 3), facecolor='#2d2d2d')
        ax.set_facecolor('#2d2d2d')
        
        bars = ax.bar(dates, durations, color='#1f6aa5', alpha=0.8)
        ax.set_title('Günlük Aktivite Süresi (dakika)', color='white', fontsize=12)
        ax.set_xlabel('Tarih', color='white')
        ax.set_ylabel('Dakika', color='white')
        
        ax.tick_params(colors='white')
        ax.spines['bottom'].set_color('#404040')
        ax.spines['left'].set_color('#404040')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        for bar, val in zip(bars, durations):
            if val > 0:
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
               f'{val:.0f} dk', ha='center', va='bottom', color='white', fontsize=9)
        
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, self.chart_content)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
    
    def _export_data(self, format_type):
        if format_type == 'json':
            filepath = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json")]
            )
            if filepath:
                self.db_manager.export_to_json(filepath)
                messagebox.showinfo("Başarılı", f"Veriler JSON'a aktarıldı:\n{filepath}")
        
        elif format_type == 'csv':
            filepath = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv")]
            )
            if filepath:
                self.db_manager.export_to_csv(filepath)
                messagebox.showinfo("Başarılı", f"Veriler CSV'ye aktarıldı:\n{filepath}")