import customtkinter as ctk
from gui.styles import AppStyles
from models import DailyActivity, ReadingDetail, WorkDetail, EducationDetail, HobbyDetail, Category
from datetime import datetime
from tkinter import messagebox
from utils.streak_tracker import StreakTracker

class ActivityForm(ctk.CTkFrame):
    def __init__(self, master, db_manager):
        super().__init__(master, fg_color=AppStyles.COLORS['background'])
        self.db_manager = db_manager
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        
        self._create_widgets()
    
    def _create_widgets(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=10)
        
        ctk.CTkLabel(
            header,
            text="➕ Aktivite Ekle",
            font=AppStyles.get_font(24, "bold")
        ).pack(side="left")
        
        self.form_frame = ctk.CTkScrollableFrame(
            self,
            fg_color=AppStyles.COLORS['surface'],
            corner_radius=10
        )
        self.form_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        
        ctk.CTkLabel(
            self.form_frame,
            text="Kategori Seçin:",
            font=AppStyles.get_font(14, "bold")
        ).pack(pady=5, padx=20, anchor="w")
        
        self.category_var = ctk.StringVar(value="Kitap / Okuma")
        categories = ["Kitap / Okuma", "İş / Proje", "Eğitim", "Hobi / Spor", "Kişisel", "Diğer"]
        
        self.category_menu = ctk.CTkOptionMenu(
            self.form_frame,
            values=categories,
            variable=self.category_var,
            command=self._on_category_change,
            font=AppStyles.get_font(13),
            height=35
        )
        self.category_menu.pack(pady=5, padx=20, fill="x")
        
        ctk.CTkLabel(
            self.form_frame,
            text="Tarih:",
            font=AppStyles.get_font(14, "bold")
        ).pack(pady=(20, 5), padx=20, anchor="w")
        
        self.date_var = ctk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        date_frame = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        date_frame.pack(pady=5, padx=20, fill="x")
        
        self.date_entry = ctk.CTkEntry(
            date_frame,
            textvariable=self.date_var,
            font=AppStyles.get_font(13),
            height=35
        )
        self.date_entry.pack(side="left", expand=True, fill="x")
        
        ctk.CTkButton(
            date_frame,
            text="Bugün",
            width=60,
            font=AppStyles.get_font(12),
            command=lambda: self.date_var.set(datetime.now().strftime("%Y-%m-%d"))
        ).pack(side="right", padx=5)
        
        ctk.CTkLabel(
            self.form_frame,
            text="Başlık:",
            font=AppStyles.get_font(14, "bold")
        ).pack(pady=(20, 5), padx=20, anchor="w")
        
        self.title_entry = ctk.CTkEntry(
            self.form_frame,
            placeholder_text="Aktivite başlığı...",
            font=AppStyles.get_font(13),
            height=35
        )
        self.title_entry.pack(pady=5, padx=20, fill="x")
        
        self.dynamic_frame = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        self.dynamic_frame.pack(fill="x", padx=20, pady=10)
        
        self._create_common_fields()
        
        ctk.CTkButton(
            self.form_frame,
            text="💾 Aktiviteyi Kaydet",
            font=AppStyles.get_font(14, "bold"),
            height=40,
            command=self._save_activity
        ).pack(pady=20, padx=20, fill="x")
        
        self._on_category_change("Kitap / Okuma")
    
    def _create_common_fields(self):
        ctk.CTkLabel(
            self.form_frame,
            text="Öncelik:",
            font=AppStyles.get_font(14, "bold")
        ).pack(pady=(20, 5), padx=20, anchor="w")
        
        self.priority_var = ctk.StringVar(value="Medium")
        priorities = ["Low", "Medium", "High"]
        
        priority_frame = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        priority_frame.pack(pady=5, padx=20, fill="x")
        
        for priority in priorities:
            ctk.CTkRadioButton(
                priority_frame,
                text=priority,
                variable=self.priority_var,
                value=priority,
                font=AppStyles.get_font(12)
            ).pack(side="left", padx=10)
        
        ctk.CTkLabel(
            self.form_frame,
            text="Durum:",
            font=AppStyles.get_font(14, "bold")
        ).pack(pady=(20, 5), padx=20, anchor="w")
        
        self.status_var = ctk.StringVar(value="In Progress")
        statuses = ["In Progress", "Completed"]
        
        self.status_menu = ctk.CTkOptionMenu(
            self.form_frame,
            values=statuses,
            variable=self.status_var,
            font=AppStyles.get_font(13),
            height=35
        )
        self.status_menu.pack(pady=5, padx=20, fill="x")
    
    def _on_category_change(self, category):
        for widget in self.dynamic_frame.winfo_children():
            widget.destroy()
        
        if category == "Kitap / Okuma":
            self._create_reading_fields()
        elif category == "İş / Proje":
            self._create_work_fields()
        elif category == "Eğitim":
            self._create_education_fields()
        elif category == "Hobi / Spor":
            self._create_hobby_fields()
        elif category in ["Kişisel", "Diğer"]:
            self._create_general_fields()
    
    def _create_reading_fields(self):
        ctk.CTkLabel(self.dynamic_frame, text="Kitap Adı:", font=AppStyles.get_font(13)).pack(pady=(10, 2), anchor="w")
        self.book_name = ctk.CTkEntry(self.dynamic_frame, placeholder_text="Kitap adı...", height=35)
        self.book_name.pack(fill="x", pady=2)
        
        ctk.CTkLabel(self.dynamic_frame, text="Okunan Sayfa Sayısı:", font=AppStyles.get_font(13)).pack(pady=(10, 2), anchor="w")
        self.pages_read = ctk.CTkEntry(self.dynamic_frame, placeholder_text="0", height=35)
        self.pages_read.pack(fill="x", pady=2)
        
        ctk.CTkLabel(self.dynamic_frame, text="Alıntılar / Notlar:", font=AppStyles.get_font(13)).pack(pady=(10, 2), anchor="w")
        self.reading_notes = ctk.CTkTextbox(self.dynamic_frame, height=100, font=AppStyles.get_font(12))
        self.reading_notes.pack(fill="x", pady=2)
    
    def _create_work_fields(self):
        ctk.CTkLabel(self.dynamic_frame, text="Proje Başlığı:", font=AppStyles.get_font(13)).pack(pady=(10, 2), anchor="w")
        self.project_title = ctk.CTkEntry(self.dynamic_frame, placeholder_text="Proje adı...", height=35)
        self.project_title.pack(fill="x", pady=2)
        
        ctk.CTkLabel(self.dynamic_frame, text="Tamamlanan Kısımlar:", font=AppStyles.get_font(13)).pack(pady=(10, 2), anchor="w")
        self.completed_tasks = ctk.CTkTextbox(self.dynamic_frame, height=80, font=AppStyles.get_font(12))
        self.completed_tasks.pack(fill="x", pady=2)
        
        ctk.CTkLabel(self.dynamic_frame, text="Eksik Kısımlar:", font=AppStyles.get_font(13)).pack(pady=(10, 2), anchor="w")
        self.pending_tasks = ctk.CTkTextbox(self.dynamic_frame, height=80, font=AppStyles.get_font(12))
        self.pending_tasks.pack(fill="x", pady=2)
        
        ctk.CTkLabel(self.dynamic_frame, text="Harcanan Süre (saat):", font=AppStyles.get_font(13)).pack(pady=(10, 2), anchor="w")
        self.work_duration = ctk.CTkEntry(self.dynamic_frame, placeholder_text="0", height=35)
        self.work_duration.pack(fill="x", pady=2)
    
    def _create_education_fields(self):
        ctk.CTkLabel(self.dynamic_frame, text="Kurs/Eğitim Adı:", font=AppStyles.get_font(13)).pack(pady=(10, 2), anchor="w")
        self.course_name = ctk.CTkEntry(self.dynamic_frame, placeholder_text="Kurs adı...", height=35)
        self.course_name.pack(fill="x", pady=2)
        
        ctk.CTkLabel(self.dynamic_frame, text="Öğrenilen Konular:", font=AppStyles.get_font(13)).pack(pady=(10, 2), anchor="w")
        self.topics_learned = ctk.CTkTextbox(self.dynamic_frame, height=100, font=AppStyles.get_font(12))
        self.topics_learned.pack(fill="x", pady=2)
        
        ctk.CTkLabel(self.dynamic_frame, text="Harcanan Süre (saat):", font=AppStyles.get_font(13)).pack(pady=(10, 2), anchor="w")
        self.education_duration = ctk.CTkEntry(self.dynamic_frame, placeholder_text="0", height=35)
        self.education_duration.pack(fill="x", pady=2)
    
    def _create_hobby_fields(self):
        ctk.CTkLabel(self.dynamic_frame, text="Aktivite Adı:", font=AppStyles.get_font(13)).pack(pady=(10, 2), anchor="w")
        self.hobby_name = ctk.CTkEntry(self.dynamic_frame, placeholder_text="Aktivite adı...", height=35)
        self.hobby_name.pack(fill="x", pady=2)
        
        ctk.CTkLabel(self.dynamic_frame, text="Açıklama:", font=AppStyles.get_font(13)).pack(pady=(10, 2), anchor="w")
        self.hobby_description = ctk.CTkTextbox(self.dynamic_frame, height=80, font=AppStyles.get_font(12))
        self.hobby_description.pack(fill="x", pady=2)
        
        ctk.CTkLabel(self.dynamic_frame, text="Süre (dakika):", font=AppStyles.get_font(13)).pack(pady=(10, 2), anchor="w")
        self.hobby_duration = ctk.CTkEntry(self.dynamic_frame, placeholder_text="0", height=35)
        self.hobby_duration.pack(fill="x", pady=2)
    
    def _create_general_fields(self):
        ctk.CTkLabel(self.dynamic_frame, text="Açıklama:", font=AppStyles.get_font(13)).pack(pady=(10, 2), anchor="w")
        self.general_description = ctk.CTkTextbox(self.dynamic_frame, height=100, font=AppStyles.get_font(12))
        self.general_description.pack(fill="x", pady=2)
        
        ctk.CTkLabel(self.dynamic_frame, text="Süre (dakika):", font=AppStyles.get_font(13)).pack(pady=(10, 2), anchor="w")
        self.general_duration = ctk.CTkEntry(self.dynamic_frame, placeholder_text="0", height=35)
        self.general_duration.pack(fill="x", pady=2)
    
    def _save_activity(self):
        try:
            if not self.title_entry.get().strip():
                messagebox.showwarning("Uyarı", "Başlık alanı zorunludur!")
                return
            
            session = self.db_manager.get_session()
            
            try:
                category = session.query(Category).filter_by(
                    name=self.category_var.get()
                ).first()
                
                activity = DailyActivity(
                    date=datetime.strptime(self.date_var.get(), "%Y-%m-%d").date(),
                    category_id=category.id,
                    title=self.title_entry.get(),
                    description="",
                    priority=self.priority_var.get(),
                    status=self.status_var.get()
                )
                
                category_name = self.category_var.get()
                
                if category_name == "Kitap / Okuma":
                    pages = self.pages_read.get()
                    activity.duration_minutes = int(pages) * 2 if pages.isdigit() else 0
                    
                    detail = ReadingDetail(
                        book_name=self.book_name.get(),
                        pages_read=int(pages) if pages.isdigit() else 0,
                        quotes=self.reading_notes.get("1.0", "end-1c"),
                        activity=activity
                    )
                    session.add(detail)
                    
                elif category_name == "İş / Proje":
                    hours = self.work_duration.get()
                    activity.duration_minutes = int(float(hours) * 60) if hours.replace('.', '').isdigit() else 0
                    
                    detail = WorkDetail(
                        project_title=self.project_title.get(),
                        completed_tasks=self.completed_tasks.get("1.0", "end-1c"),
                        pending_tasks=self.pending_tasks.get("1.0", "end-1c"),
                        duration_hours=float(hours) if hours.replace('.', '').isdigit() else 0,
                        activity=activity
                    )
                    session.add(detail)
                    
                elif category_name == "Eğitim":
                    hours = self.education_duration.get()
                    activity.duration_minutes = int(float(hours) * 60) if hours.replace('.', '').isdigit() else 0
                    
                    detail = EducationDetail(
                        course_name=self.course_name.get(),
                        topics_learned=self.topics_learned.get("1.0", "end-1c"),
                        duration_hours=float(hours) if hours.replace('.', '').isdigit() else 0,
                        activity=activity
                    )
                    session.add(detail)
                    
                elif category_name == "Hobi / Spor":
                    minutes = self.hobby_duration.get()
                    activity.duration_minutes = int(minutes) if minutes.isdigit() else 0
                    
                    detail = HobbyDetail(
                        activity_name=self.hobby_name.get(),
                        description=self.hobby_description.get("1.0", "end-1c"),
                        duration_minutes=int(minutes) if minutes.isdigit() else 0,
                        activity=activity
                    )
                    session.add(detail)
                    
                elif category_name in ["Kişisel", "Diğer"]:
                    minutes = self.general_duration.get()
                    activity.duration_minutes = int(minutes) if minutes.isdigit() else 0
                    activity.description = self.general_description.get("1.0", "end-1c")
                
                session.add(activity)
                session.commit()
                
                tracker = StreakTracker(self.db_manager)
                tracker.update_streak(category.id)
                
                messagebox.showinfo("Başarılı", "Aktivite başarıyla kaydedildi!")
                self._clear_form()
                
            except Exception as e:
                session.rollback()
                messagebox.showerror("Hata", f"Kayıt sırasında hata oluştu:\n{str(e)}")
            finally:
                session.close()
                
        except Exception as e:
            messagebox.showerror("Hata", f"Beklenmeyen hata:\n{str(e)}")
    
    def _clear_form(self):
        self.title_entry.delete(0, 'end')
        self.priority_var.set("Medium")
        self.status_var.set("In Progress")
        self._on_category_change(self.category_var.get())