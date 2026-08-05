import customtkinter as ctk
from gui.styles import AppStyles
from models import WeeklyPlan
from datetime import datetime, timedelta
from tkinter import messagebox

class WeeklyPlanner(ctk.CTkFrame):
    def __init__(self, master, db_manager):
        super().__init__(master, fg_color=AppStyles.COLORS['background'])
        self.db_manager = db_manager
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=1)
        
        self._create_widgets()
        
        self.current_week_start = datetime.now().date()
        self.current_week_start -= timedelta(days=self.current_week_start.weekday())
        
        self.refresh_plans()
    
    def _create_widgets(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=10)
        
        ctk.CTkLabel(
            header,
            text="📅 Haftalık Planlayıcı",
            font=AppStyles.get_font(24, "bold")
        ).pack(side="left")
        
        nav_frame = ctk.CTkFrame(header, fg_color="transparent")
        nav_frame.pack(side="right")
        
        self.week_label = ctk.CTkLabel(nav_frame, text="", font=AppStyles.get_font(14))
        self.week_label.pack(side="left", padx=10)
        
        ctk.CTkButton(nav_frame, text="◀", width=40, command=self._previous_week).pack(side="left", padx=2)
        ctk.CTkButton(nav_frame, text="▶", width=40, command=self._next_week).pack(side="left", padx=2)
        ctk.CTkButton(
            nav_frame,
            text="↻ Aktarılmayanları Devret",
            font=AppStyles.get_font(12),
            command=self._transfer_incomplete
        ).pack(side="left", padx=10)
        
        add_frame = ctk.CTkFrame(self, fg_color=AppStyles.COLORS['surface'])
        add_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 10))
        
        ctk.CTkLabel(add_frame, text="Yeni Plan Ekle", font=AppStyles.get_font(14, "bold")).pack(pady=5, padx=20, anchor="w")
        
        form_row = ctk.CTkFrame(add_frame, fg_color="transparent")
        form_row.pack(fill="x", padx=20, pady=5)
        
        days = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
        self.day_var = ctk.StringVar(value=days[datetime.now().weekday()])
        ctk.CTkOptionMenu(form_row, values=days, variable=self.day_var, width=120, font=AppStyles.get_font(12)).pack(side="left", padx=5)
        
        self.plan_title = ctk.CTkEntry(form_row, placeholder_text="Plan başlığı...", font=AppStyles.get_font(12))
        self.plan_title.pack(side="left", padx=5, expand=True, fill="x")
        
        self.plan_priority = ctk.StringVar(value="Medium")
        ctk.CTkOptionMenu(form_row, values=["Low", "Medium", "High"], variable=self.plan_priority, width=80, font=AppStyles.get_font(12)).pack(side="left", padx=5)
        
        ctk.CTkButton(form_row, text="➕ Ekle", width=60, font=AppStyles.get_font(12), command=self._add_plan).pack(side="left", padx=5)
        
        self.plans_frame = ctk.CTkScrollableFrame(self, fg_color=AppStyles.COLORS['surface'])
        self.plans_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0, 10))
    
    def _previous_week(self):
        self.current_week_start -= timedelta(days=7)
        self.refresh_plans()
    
    def _next_week(self):
        self.current_week_start += timedelta(days=7)
        self.refresh_plans()
    
    def _add_plan(self):
        title = self.plan_title.get().strip()
        if not title:
            messagebox.showwarning("Uyarı", "Plan başlığı gerekli!")
            return
        
        days = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
        day_index = days.index(self.day_var.get())
        
        session = self.db_manager.get_session()
        try:
            plan = WeeklyPlan(
                week_start_date=self.current_week_start,
                day_of_week=day_index,
                title=title,
                priority=self.plan_priority.get()
            )
            session.add(plan)
            session.commit()
            
            self.plan_title.delete(0, 'end')
            self.refresh_plans()
            
        finally:
            session.close()
    
    def _transfer_incomplete(self):
        if not messagebox.askyesno("Onay", "Tamamlanmamış planları sonraki haftaya aktarmak istiyor musunuz?"):
            return
        
        session = self.db_manager.get_session()
        try:
            incomplete = session.query(WeeklyPlan).filter(
                WeeklyPlan.week_start_date == self.current_week_start,
                WeeklyPlan.is_completed == False
            ).all()
            
            next_week = self.current_week_start + timedelta(days=7)
            
            for plan in incomplete:
                new_plan = WeeklyPlan(
                    week_start_date=next_week,
                    day_of_week=plan.day_of_week,
                    title=plan.title,
                    priority=plan.priority
                )
                session.add(new_plan)
                plan.is_completed = True
            
            session.commit()
            messagebox.showinfo("Başarılı", f"{len(incomplete)} plan sonraki haftaya aktarıldı.")
            
        finally:
            session.close()
    
    def refresh_plans(self):
        for widget in self.plans_frame.winfo_children():
            widget.destroy()
        
        week_end = self.current_week_start + timedelta(days=6)
        self.week_label.configure(
            text=f"{self.current_week_start.strftime('%d.%m.%Y')} - {week_end.strftime('%d.%m.%Y')}"
        )
        
        session = self.db_manager.get_session()
        try:
            days = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
            
            for day_index, day_name in enumerate(days):
                plans = session.query(WeeklyPlan).filter(
                    WeeklyPlan.week_start_date == self.current_week_start,
                    WeeklyPlan.day_of_week == day_index
                ).all()
                
                day_frame = ctk.CTkFrame(self.plans_frame, fg_color=AppStyles.COLORS['surface_hover'])
                day_frame.pack(fill="x", pady=2, padx=5)
                
                ctk.CTkLabel(
                    day_frame,
                    text=f"📌 {day_name} ({len(plans)} plan)",
                    font=AppStyles.get_font(14, "bold")
                ).pack(pady=5, padx=10, anchor="w")
                
                if plans:
                    for plan in plans:
                        plan_row = ctk.CTkFrame(day_frame, fg_color="transparent")
                        plan_row.pack(fill="x", padx=20, pady=2)
                        
                        checkbox = ctk.CTkCheckBox(
                            plan_row,
                            text="",
                            width=20,
                            command=lambda p=plan: self._toggle_plan(p)
                        )
                        checkbox.pack(side="left")
                        
                        if plan.is_completed:
                            checkbox.select()
                        
                        title_text = f"✓ {plan.title}" if plan.is_completed else plan.title
                        ctk.CTkLabel(plan_row, text=title_text, font=AppStyles.get_font(13)).pack(side="left", padx=5)
                        
                        priority_colors = {'Low': 'green', 'Medium': 'orange', 'High': 'red'}
                        ctk.CTkLabel(
                            plan_row,
                            text=f"● {plan.priority}",
                            font=AppStyles.get_font(11),
                            text_color=priority_colors.get(plan.priority, 'white')
                        ).pack(side="left", padx=10)
                        
                        ctk.CTkButton(
                            plan_row,
                            text="🗑",
                            width=30,
                            height=25,
                            fg_color="transparent",
                            hover_color=AppStyles.COLORS['error'],
                            command=lambda p=plan: self._delete_plan(p)
                        ).pack(side="right")
                else:
                    ctk.CTkLabel(
                        day_frame,
                        text="Plan yok",
                        font=AppStyles.get_font(12),
                        text_color=AppStyles.COLORS['text_secondary']
                    ).pack(pady=5, padx=30, anchor="w")
                    
        finally:
            session.close()
    
    def _toggle_plan(self, plan):
        session = self.db_manager.get_session()
        try:
            plan = session.merge(plan)
            plan.is_completed = not plan.is_completed
            session.commit()
            self.refresh_plans()
        finally:
            session.close()
    
    def _delete_plan(self, plan):
        if messagebox.askyesno("Onay", "Bu planı silmek istiyor musunuz?"):
            session = self.db_manager.get_session()
            try:
                plan = session.merge(plan)
                session.delete(plan)
                session.commit()
                self.refresh_plans()
            finally:
                session.close()