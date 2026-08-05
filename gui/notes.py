import customtkinter as ctk
from gui.styles import AppStyles
from models import Note, WeeklyPlan
from datetime import datetime, timedelta
from tkinter import messagebox

class NotesPage(ctk.CTkFrame):
    def __init__(self, master, db_manager):
        super().__init__(master, fg_color=AppStyles.COLORS['background'])
        self.db_manager = db_manager
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        
        self._create_widgets()
        self.refresh_notes()
    
    def _create_widgets(self):
        # Başlık
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=20, pady=10)
        
        ctk.CTkLabel(header, text="📝 Notlar", font=AppStyles.get_font(24, "bold")).pack(side="left")
        ctk.CTkButton(header, text="➕ Yeni Not", font=AppStyles.get_font(12), command=self._show_note_form).pack(side="right")
        
        # Not listesi (sol)
        self.notes_list = ctk.CTkScrollableFrame(self, fg_color=AppStyles.COLORS['surface'])
        self.notes_list.grid(row=1, column=0, sticky="nsew", padx=(20, 10), pady=10)
        
        ctk.CTkLabel(self.notes_list, text="Notlarım", font=AppStyles.get_font(16, "bold")).pack(pady=10, padx=20, anchor="w")
        
        self.notes_content = ctk.CTkFrame(self.notes_list, fg_color="transparent")
        self.notes_content.pack(fill="both", expand=True, padx=10)
        
        # Not detayı (sağ)
        self.note_detail = AppStyles.create_card_frame(self)
        self.note_detail.grid(row=1, column=1, sticky="nsew", padx=(10, 20), pady=10)
        
        ctk.CTkLabel(self.note_detail, text="Not Detayı", font=AppStyles.get_font(16, "bold")).pack(pady=10, padx=20, anchor="w")
        
        self.detail_content = ctk.CTkFrame(self.note_detail, fg_color="transparent")
        self.detail_content.pack(fill="both", expand=True, padx=20, pady=10)
        
        ctk.CTkLabel(
            self.detail_content,
            text="Bir not seçin",
            font=AppStyles.get_font(14),
            text_color=AppStyles.COLORS['text_secondary']
        ).pack(expand=True)
    
    def _show_note_form(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Yeni Not")
        dialog.geometry("500x400")
        dialog.grab_set()
        
        ctk.CTkLabel(dialog, text="Başlık:", font=AppStyles.get_font(13)).pack(pady=5, padx=20, anchor="w")
        title_entry = ctk.CTkEntry(dialog, font=AppStyles.get_font(12))
        title_entry.pack(pady=5, padx=20, fill="x")
        
        ctk.CTkLabel(dialog, text="İçerik:", font=AppStyles.get_font(13)).pack(pady=5, padx=20, anchor="w")
        content_text = ctk.CTkTextbox(dialog, height=150, font=AppStyles.get_font(12))
        content_text.pack(pady=5, padx=20, fill="both", expand=True)
        
        def save_note():
            title = title_entry.get().strip()
            content = content_text.get("1.0", "end-1c").strip()
            
            if not title:
                messagebox.showwarning("Uyarı", "Başlık gerekli!")
                return
            
            session = self.db_manager.get_session()
            try:
                note = Note(title=title, content=content)
                session.add(note)
                session.commit()
                
                dialog.destroy()
                self.refresh_notes()
                
            finally:
                session.close()
        
        ctk.CTkButton(dialog, text="💾 Kaydet", font=AppStyles.get_font(13), command=save_note).pack(pady=10)
    
    def refresh_notes(self):
        for widget in self.notes_content.winfo_children():
            widget.destroy()
        
        session = self.db_manager.get_session()
        try:
            notes = session.query(Note).order_by(Note.created_at.desc()).all()
            
            if not notes:
                ctk.CTkLabel(
                    self.notes_content,
                    text="Henüz not yok",
                    font=AppStyles.get_font(14),
                    text_color=AppStyles.COLORS['text_secondary']
                ).pack(pady=20)
            else:
                for note in notes:
                    note_frame = ctk.CTkFrame(self.notes_content, fg_color=AppStyles.COLORS['surface_hover'])
                    note_frame.pack(fill="x", pady=2)
                    
                    ctk.CTkLabel(note_frame, text=note.title, font=AppStyles.get_font(13, "bold")).pack(pady=5, padx=10, anchor="w")
                    
                    date_text = note.created_at.strftime("%d.%m.%Y %H:%M")
                    ctk.CTkLabel(
                        note_frame,
                        text=date_text,
                        font=AppStyles.get_font(11),
                        text_color=AppStyles.COLORS['text_secondary']
                    ).pack(pady=2, padx=10, anchor="w")
                    
                    btn_frame = ctk.CTkFrame(note_frame, fg_color="transparent")
                    btn_frame.pack(pady=5, padx=10, fill="x")
                    
                    ctk.CTkButton(
                        btn_frame,
                        text="Görüntüle",
                        font=AppStyles.get_font(11),
                        width=70,
                        height=25,
                        command=lambda n=note: self._show_note_detail(n)
                    ).pack(side="left", padx=2)
                    
                    ctk.CTkButton(
                        btn_frame,
                        text="Plana Aktar",
                        font=AppStyles.get_font(11),
                        width=80,
                        height=25,
                        fg_color=AppStyles.COLORS['info'],
                        command=lambda n=note: self._transfer_to_planner(n)
                    ).pack(side="left", padx=2)
                    
                    ctk.CTkButton(
                        btn_frame,
                        text="Sil",
                        font=AppStyles.get_font(11),
                        width=50,
                        height=25,
                        fg_color=AppStyles.COLORS['error'],
                        command=lambda n=note: self._delete_note(n)
                    ).pack(side="right", padx=2)
                    
        finally:
            session.close()
    
    def _show_note_detail(self, note):
        for widget in self.detail_content.winfo_children():
            widget.destroy()
        
        ctk.CTkLabel(self.detail_content, text=note.title, font=AppStyles.get_font(16, "bold")).pack(pady=10, anchor="w")
        
        ctk.CTkLabel(
            self.detail_content,
            text=f"Tarih: {note.created_at.strftime('%d.%m.%Y %H:%M')}",
            font=AppStyles.get_font(12),
            text_color=AppStyles.COLORS['text_secondary']
        ).pack(anchor="w")
        
        content_frame = ctk.CTkFrame(self.detail_content, fg_color=AppStyles.COLORS['surface_hover'])
        content_frame.pack(fill="both", expand=True, pady=10)
        
        ctk.CTkLabel(
            content_frame,
            text=note.content or "İçerik yok",
            font=AppStyles.get_font(13),
            wraplength=400,
            justify="left"
        ).pack(pady=10, padx=10)
    
    def _transfer_to_planner(self, note):
        session = self.db_manager.get_session()
        try:
            today = datetime.now().date()
            week_start = today - timedelta(days=today.weekday())
            
            plan = WeeklyPlan(
                week_start_date=week_start,
                day_of_week=today.weekday(),
                title=note.title,
                description=note.content,
                priority="Medium"
            )
            session.add(plan)
            
            note.is_transferred = True
            session.commit()
            
            messagebox.showinfo("Başarılı", "Not haftalık plana aktarıldı!")
            self.refresh_notes()
            
            main_window = self.winfo_toplevel()
            if hasattr(main_window, 'show_page'):
                main_window.show_page('planner')
            
        finally:
            session.close()
    
    def _delete_note(self, note):
        if messagebox.askyesno("Onay", "Bu notu silmek istiyor musunuz?"):
            session = self.db_manager.get_session()
            try:
                session.delete(note)
                session.commit()
                self.refresh_notes()
                
                # Detay panelini temizle
                for widget in self.detail_content.winfo_children():
                    widget.destroy()
                ctk.CTkLabel(
                    self.detail_content,
                    text="Bir not seçin",
                    font=AppStyles.get_font(14),
                    text_color=AppStyles.COLORS['text_secondary']
                ).pack(expand=True)
                
            finally:
                session.close()