import customtkinter as ctk
from gui.dashboard import Dashboard
from gui.activity_form import ActivityForm
from gui.weekly_planner import WeeklyPlanner
from gui.notes import NotesPage
from gui.analytics import AnalyticsPage
from gui.history import HistoryPage
from gui.styles import AppStyles

class MainWindow(ctk.CTk):
    def __init__(self, db_manager):
        super().__init__()
        
        self.db_manager = db_manager
        self.title("Kişisel Planlayıcı ve Aktivite Takip")
        self.geometry("1400x800")
        self.minsize(1200, 700)
        
        AppStyles.setup_theme()
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        self._create_sidebar()
        
        self.content_area = ctk.CTkFrame(self, fg_color=AppStyles.COLORS['background'])
        self.content_area.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        self.content_area.grid_rowconfigure(0, weight=1)
        self.content_area.grid_columnconfigure(0, weight=1)
        
        self.pages = {}
        self._load_pages()
        self.show_page("dashboard")
    
    def _create_sidebar(self):
        sidebar = ctk.CTkFrame(
            self, 
            width=250, 
            corner_radius=0,
            fg_color=AppStyles.COLORS['surface']
        )
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)
        
        logo_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        logo_frame.pack(pady=20, padx=20, fill="x")
        
        ctk.CTkLabel(
            logo_frame,
            text="📋 Planner",
            font=AppStyles.get_font(24, "bold"),
            text_color=AppStyles.COLORS['text']
        ).pack(anchor="w")
        
        ctk.CTkFrame(sidebar, height=2, fg_color="#404040").pack(fill="x", padx=20, pady=10)
        
        nav_buttons = [
            ("📊 Dashboard", "dashboard"),
            ("➕ Aktivite Ekle", "activity"),
            ("📅 Haftalık Plan", "planner"),
            ("📝 Notlar", "notes"),
            ("📈 Analiz", "analytics"),
            ("📋 Geçmiş", "history")
        ]
        
        self.nav_buttons = {}
        for text, page_name in nav_buttons:
            btn = ctk.CTkButton(
                sidebar,
                text=text,
                font=AppStyles.get_font(14),
                fg_color="transparent",
                hover_color=AppStyles.COLORS['primary'],
                anchor="w",
                height=40,
                command=lambda p=page_name: self.show_page(p)
            )
            btn.pack(pady=5, padx=20, fill="x")
            self.nav_buttons[page_name] = btn
        
        ctk.CTkFrame(sidebar, fg_color="transparent").pack(side="bottom", pady=20, padx=20, fill="x")
        
        ctk.CTkButton(
            sidebar,
            text="💾 Yedekle",
            font=AppStyles.get_font(12),
            fg_color=AppStyles.COLORS['secondary'],
            hover_color=AppStyles.COLORS['primary'],
            command=self._backup_database
        ).pack(side="bottom", pady=10, padx=20, fill="x")
    
    def _load_pages(self):
        self.pages = {
            "dashboard": Dashboard(self.content_area, self.db_manager),
            "activity": ActivityForm(self.content_area, self.db_manager),
            "planner": WeeklyPlanner(self.content_area, self.db_manager),
            "notes": NotesPage(self.content_area, self.db_manager),
            "analytics": AnalyticsPage(self.content_area, self.db_manager),
            "history": HistoryPage(self.content_area, self.db_manager)
        }
    
    def show_page(self, page_name):
        for name, btn in self.nav_buttons.items():
            if name == page_name:
                btn.configure(fg_color=AppStyles.COLORS['primary'])
            else:
                btn.configure(fg_color="transparent")
        
        for name, page in self.pages.items():
            if name == page_name:
                page.pack(fill="both", expand=True)
                if hasattr(page, 'refresh_data'):
                    page.refresh_data()
                if hasattr(page, 'refresh_analytics'):
                    page.refresh_analytics()
            else:
                page.pack_forget()
    
    def _backup_database(self):
        from tkinter import messagebox
        
        try:
            backup_path = self.db_manager.backup_database()
            messagebox.showinfo("Başarılı", f"Veritabanı yedeklendi:\n{backup_path}")
        except Exception as e:
            messagebox.showerror("Hata", f"Yedekleme başarısız:\n{str(e)}")