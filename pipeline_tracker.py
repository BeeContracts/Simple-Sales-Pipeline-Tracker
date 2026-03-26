#!/usr/bin/env python3
"""Sales Pipeline Tracker GUI app.

A lightweight desktop app for tracking leads, stages, follow-up dates,
status filters, dashboard stats, and exporting pipeline data to JSON/CSV.
"""

from __future__ import annotations

import csv
import json
import uuid
from dataclasses import asdict, dataclass
from datetime import date, datetime
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

APP_BG = '#0f172a'
PANEL_BG = '#111827'
TEXT = '#e5e7eb'
MUTED = '#94a3b8'
ACCENT = '#38bdf8'
BUTTON = '#1f2937'
ENTRY_BG = '#1f2937'
OVERDUE = '#7f1d1d'
DUE_SOON = '#78350f'
GOOD = '#14532d'

STAGES = ['New Lead', 'Contacted', 'Qualified', 'Proposal Sent', 'Negotiation', 'Closed Won', 'Closed Lost']
ACTIVE_STAGES = {'New Lead', 'Contacted', 'Qualified', 'Proposal Sent', 'Negotiation'}


@dataclass
class Lead:
    id: str
    name: str
    company: str
    email: str
    phone: str
    stage: str
    follow_up_date: str
    value: str
    notes: str


class PipelineApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title('Sales Pipeline Tracker')
        self.root.geometry('1240x820')
        self.root.configure(bg=APP_BG)
        self.data_path = Path('pipeline_data.json')
        self.leads: list[Lead] = []
        self.selected_id: str | None = None
        self._set_icon_if_available()
        self._build_ui()
        self.load_data(silent=True)
        self.refresh_table()

    def _set_icon_if_available(self) -> None:
        icon = Path(__file__).with_name('app_icon.png')
        if icon.exists():
            try:
                photo = tk.PhotoImage(file=str(icon))
                self.root.iconphoto(True, photo)
                self._icon_ref = photo
            except Exception:
                pass

    def _button(self, parent, text, command, bold=False):
        return tk.Button(parent, text=text, command=command, bg=BUTTON, fg=TEXT, activebackground=ACCENT, activeforeground='black', relief='flat', padx=10, pady=6, font=('Segoe UI', 10, 'bold' if bold else 'normal'))

    def _stat_card(self, parent, title: str, var: tk.StringVar, bg_color: str):
        frame = tk.Frame(parent, bg=bg_color, padx=12, pady=10)
        tk.Label(frame, text=title, font=('Segoe UI', 9, 'bold'), bg=bg_color, fg=TEXT).pack(anchor='w')
        tk.Label(frame, textvariable=var, font=('Segoe UI', 18, 'bold'), bg=bg_color, fg='white').pack(anchor='w', pady=(4, 0))
        return frame

    def _build_ui(self) -> None:
        tk.Label(self.root, text='Sales Pipeline Tracker', font=('Segoe UI', 18, 'bold'), bg=APP_BG, fg=TEXT).pack(pady=(12, 4))
        tk.Label(self.root, text='Track leads, stages, follow-up dates, dashboard metrics, and export your pipeline cleanly.', font=('Segoe UI', 10), bg=APP_BG, fg=MUTED).pack(pady=(0, 10))

        stats = tk.Frame(self.root, bg=APP_BG)
        stats.pack(fill='x', padx=12, pady=(0, 10))
        self.total_var = tk.StringVar(value='0')
        self.active_var = tk.StringVar(value='0')
        self.overdue_var = tk.StringVar(value='0')
        self.pipeline_value_var = tk.StringVar(value='$0')
        self._stat_card(stats, 'Total Leads', self.total_var, '#1d4ed8').pack(side='left', fill='x', expand=True, padx=(0, 6))
        self._stat_card(stats, 'Active Deals', self.active_var, GOOD).pack(side='left', fill='x', expand=True, padx=6)
        self._stat_card(stats, 'Overdue Follow-Ups', self.overdue_var, OVERDUE).pack(side='left', fill='x', expand=True, padx=6)
        self._stat_card(stats, 'Open Pipeline Value', self.pipeline_value_var, '#0f766e').pack(side='left', fill='x', expand=True, padx=(6, 0))

        top = tk.Frame(self.root, bg=APP_BG)
        top.pack(fill='both', expand=True, padx=12)

        form = tk.Frame(top, bg=PANEL_BG, padx=12, pady=12)
        form.pack(side='left', fill='y', padx=(0, 8))
        table_wrap = tk.Frame(top, bg=APP_BG)
        table_wrap.pack(side='left', fill='both', expand=True)

        self.entries = {}
        fields = [
            ('Lead Name', 'name'),
            ('Company', 'company'),
            ('Email', 'email'),
            ('Phone', 'phone'),
            ('Follow-Up Date (YYYY-MM-DD)', 'follow_up_date'),
            ('Estimated Value', 'value'),
        ]

        tk.Label(form, text='Lead Details', font=('Segoe UI', 12, 'bold'), bg=PANEL_BG, fg=TEXT).grid(row=0, column=0, columnspan=2, sticky='w', pady=(0, 10))

        row = 1
        for label, key in fields:
            tk.Label(form, text=label, bg=PANEL_BG, fg=TEXT, anchor='w').grid(row=row, column=0, sticky='w', pady=4)
            entry = tk.Entry(form, bg=ENTRY_BG, fg=TEXT, insertbackground=TEXT, relief='flat', width=28)
            entry.grid(row=row, column=1, sticky='ew', pady=4, padx=(8, 0))
            self.entries[key] = entry
            row += 1

        tk.Label(form, text='Stage', bg=PANEL_BG, fg=TEXT, anchor='w').grid(row=row, column=0, sticky='w', pady=4)
        self.stage_var = tk.StringVar(value=STAGES[0])
        self.stage_menu = ttk.Combobox(form, textvariable=self.stage_var, values=STAGES, state='readonly', width=25)
        self.stage_menu.grid(row=row, column=1, sticky='ew', pady=4, padx=(8, 0))
        row += 1

        tk.Label(form, text='Notes', bg=PANEL_BG, fg=TEXT, anchor='w').grid(row=row, column=0, sticky='nw', pady=4)
        self.notes = tk.Text(form, height=7, width=28, bg=ENTRY_BG, fg=TEXT, insertbackground=TEXT, relief='flat')
        self.notes.grid(row=row, column=1, sticky='ew', pady=4, padx=(8, 0))
        row += 1

        btns = tk.Frame(form, bg=PANEL_BG)
        btns.grid(row=row, column=0, columnspan=2, sticky='ew', pady=(10, 4))
        self._button(btns, 'Add Lead', self.add_lead, bold=True).pack(side='left')
        self._button(btns, 'Update Lead', self.update_lead).pack(side='left', padx=6)
        self._button(btns, 'Clear Form', self.clear_form).pack(side='left')
        row += 1

        actions = tk.Frame(form, bg=PANEL_BG)
        actions.grid(row=row, column=0, columnspan=2, sticky='ew', pady=6)
        self._button(actions, 'Delete Lead', self.delete_lead).pack(side='left')
        self._button(actions, 'Save JSON', self.save_json).pack(side='left', padx=6)
        self._button(actions, 'Export CSV', self.export_csv).pack(side='left')
        row += 1

        loadbar = tk.Frame(form, bg=PANEL_BG)
        loadbar.grid(row=row, column=0, columnspan=2, sticky='ew', pady=6)
        self._button(loadbar, 'Load JSON', self.load_json_prompt).pack(side='left')
        self._button(loadbar, 'Open Data Folder', self.show_data_path).pack(side='left', padx=6)

        form.grid_columnconfigure(1, weight=1)

        controls = tk.Frame(table_wrap, bg=APP_BG)
        controls.pack(fill='x', pady=(0, 8))
        tk.Label(controls, text='Filter by Stage:', bg=APP_BG, fg=TEXT).pack(side='left')
        self.filter_var = tk.StringVar(value='All')
        filter_values = ['All'] + STAGES
        self.filter_menu = ttk.Combobox(controls, textvariable=self.filter_var, values=filter_values, state='readonly', width=18)
        self.filter_menu.pack(side='left', padx=8)
        self.filter_menu.bind('<<ComboboxSelected>>', lambda e: self.refresh_table())
        self._button(controls, 'Reset Filter', self.reset_filter).pack(side='left')
        tk.Label(controls, text='Rows in red are overdue. Gold rows are due within 3 days.', bg=APP_BG, fg=MUTED).pack(side='right')

        cols = ('name', 'company', 'email', 'phone', 'stage', 'follow_up_date', 'value')
        self.tree = ttk.Treeview(table_wrap, columns=cols, show='headings', height=24)
        for col, width in [('name', 150), ('company', 160), ('email', 190), ('phone', 120), ('stage', 120), ('follow_up_date', 120), ('value', 100)]:
            self.tree.heading(col, text=col.replace('_', ' ').title())
            self.tree.column(col, width=width, anchor='w')
        self.tree.pack(fill='both', expand=True)
        self.tree.bind('<<TreeviewSelect>>', self.on_select)

        style = ttk.Style()
        try:
            style.theme_use('default')
        except Exception:
            pass
        style.configure('Treeview', background=PANEL_BG, fieldbackground=PANEL_BG, foreground=TEXT, rowheight=28)
        style.configure('Treeview.Heading', background=BUTTON, foreground=TEXT)
        style.map('Treeview', background=[('selected', ACCENT)], foreground=[('selected', 'black')])
        self.tree.tag_configure('overdue', background=OVERDUE, foreground='white')
        self.tree.tag_configure('due_soon', background=DUE_SOON, foreground='white')

        self.status_var = tk.StringVar(value='Ready')
        tk.Label(self.root, textvariable=self.status_var, anchor='w', bg=APP_BG, fg=MUTED).pack(fill='x', padx=12, pady=(6, 10))

    def set_status(self, text: str) -> None:
        self.status_var.set(text)

    def clear_form(self) -> None:
        for entry in self.entries.values():
            entry.delete(0, tk.END)
        self.stage_var.set(STAGES[0])
        self.notes.delete('1.0', tk.END)
        self.selected_id = None
        self.set_status('Form cleared')

    def get_form_data(self) -> Lead | None:
        name = self.entries['name'].get().strip()
        company = self.entries['company'].get().strip()
        email = self.entries['email'].get().strip()
        phone = self.entries['phone'].get().strip()
        follow_up_date = self.entries['follow_up_date'].get().strip()
        value = self.entries['value'].get().strip()
        stage = self.stage_var.get().strip()
        notes = self.notes.get('1.0', tk.END).strip()

        if not name or not company:
            messagebox.showwarning('Missing Info', 'Lead Name and Company are required.')
            return None

        if follow_up_date:
            try:
                datetime.strptime(follow_up_date, '%Y-%m-%d')
            except ValueError:
                messagebox.showwarning('Invalid Date', 'Follow-up date must be YYYY-MM-DD.')
                return None

        lead_id = self.selected_id or str(uuid.uuid4())
        return Lead(lead_id, name, company, email, phone, stage, follow_up_date, value, notes)

    def add_lead(self) -> None:
        lead = self.get_form_data()
        if not lead:
            return
        self.leads.append(lead)
        self.save_data()
        self.refresh_table()
        self.clear_form()
        self.set_status(f'Added lead: {lead.name}')

    def update_lead(self) -> None:
        if not self.selected_id:
            messagebox.showinfo('Select Lead', 'Select a lead from the table first.')
            return
        lead = self.get_form_data()
        if not lead:
            return
        for idx, existing in enumerate(self.leads):
            if existing.id == self.selected_id:
                self.leads[idx] = lead
                break
        self.save_data()
        self.refresh_table()
        self.set_status(f'Updated lead: {lead.name}')

    def delete_lead(self) -> None:
        if not self.selected_id:
            messagebox.showinfo('Select Lead', 'Select a lead from the table first.')
            return
        item = next((x for x in self.leads if x.id == self.selected_id), None)
        if not item:
            return
        if not messagebox.askyesno('Delete Lead', f'Delete {item.name} from the pipeline?'):
            return
        self.leads = [x for x in self.leads if x.id != self.selected_id]
        self.save_data()
        self.refresh_table()
        self.clear_form()
        self.set_status(f'Deleted lead: {item.name}')

    def on_select(self, _event=None) -> None:
        selected = self.tree.selection()
        if not selected:
            return
        item_id = selected[0]
        lead = next((x for x in self.leads if x.id == item_id), None)
        if not lead:
            return
        self.selected_id = lead.id
        self.entries['name'].delete(0, tk.END); self.entries['name'].insert(0, lead.name)
        self.entries['company'].delete(0, tk.END); self.entries['company'].insert(0, lead.company)
        self.entries['email'].delete(0, tk.END); self.entries['email'].insert(0, lead.email)
        self.entries['phone'].delete(0, tk.END); self.entries['phone'].insert(0, lead.phone)
        self.entries['follow_up_date'].delete(0, tk.END); self.entries['follow_up_date'].insert(0, lead.follow_up_date)
        self.entries['value'].delete(0, tk.END); self.entries['value'].insert(0, lead.value)
        self.stage_var.set(lead.stage)
        self.notes.delete('1.0', tk.END); self.notes.insert('1.0', lead.notes)
        self.set_status(f'Selected lead: {lead.name}')

    def filtered_leads(self) -> list[Lead]:
        stage_filter = self.filter_var.get()
        if stage_filter == 'All':
            return self.leads
        return [lead for lead in self.leads if lead.stage == stage_filter]

    def parse_date(self, raw: str):
        if not raw:
            return None
        try:
            return datetime.strptime(raw, '%Y-%m-%d').date()
        except ValueError:
            return None

    def money_value(self, raw: str) -> float:
        cleaned = ''.join(ch for ch in raw if ch.isdigit() or ch in '.-')
        try:
            return float(cleaned) if cleaned else 0.0
        except ValueError:
            return 0.0

    def update_stats(self) -> None:
        today = date.today()
        active = [lead for lead in self.leads if lead.stage in ACTIVE_STAGES]
        overdue = [lead for lead in active if (d := self.parse_date(lead.follow_up_date)) and d < today]
        open_value = sum(self.money_value(lead.value) for lead in active)
        self.total_var.set(str(len(self.leads)))
        self.active_var.set(str(len(active)))
        self.overdue_var.set(str(len(overdue)))
        self.pipeline_value_var.set(f'${open_value:,.0f}')

    def refresh_table(self) -> None:
        for row in self.tree.get_children():
            self.tree.delete(row)
        today = date.today()
        visible = self.filtered_leads()
        for lead in visible:
            tags = ()
            due_date = self.parse_date(lead.follow_up_date)
            if due_date and lead.stage in ACTIVE_STAGES:
                if due_date < today:
                    tags = ('overdue',)
                elif 0 <= (due_date - today).days <= 3:
                    tags = ('due_soon',)
            self.tree.insert('', tk.END, iid=lead.id, values=(lead.name, lead.company, lead.email, lead.phone, lead.stage, lead.follow_up_date, lead.value), tags=tags)
        self.update_stats()
        self.set_status(f'{len(visible)} lead(s) shown')

    def reset_filter(self) -> None:
        self.filter_var.set('All')
        self.refresh_table()

    def save_data(self) -> None:
        self.data_path.write_text(json.dumps([asdict(x) for x in self.leads], indent=2), encoding='utf-8')

    def load_data(self, silent: bool = False) -> None:
        if not self.data_path.exists():
            if not silent:
                self.set_status('No saved data found yet')
            return
        try:
            raw = json.loads(self.data_path.read_text(encoding='utf-8'))
            self.leads = [Lead(**item) for item in raw]
            if not silent:
                self.set_status(f'Loaded {len(self.leads)} lead(s)')
        except Exception as e:
            if not silent:
                messagebox.showerror('Load Error', f'Could not load saved data: {e}')

    def save_json(self) -> None:
        path = filedialog.asksaveasfilename(defaultextension='.json', filetypes=[('JSON files', '*.json')], initialfile='sales_pipeline.json')
        if not path:
            return
        Path(path).write_text(json.dumps([asdict(x) for x in self.leads], indent=2), encoding='utf-8')
        self.set_status(f'Saved JSON: {path}')

    def export_csv(self) -> None:
        path = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[('CSV files', '*.csv')], initialfile='sales_pipeline.csv')
        if not path:
            return
        with open(path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['id', 'name', 'company', 'email', 'phone', 'stage', 'follow_up_date', 'value', 'notes'])
            writer.writeheader()
            for lead in self.leads:
                writer.writerow(asdict(lead))
        self.set_status(f'Exported CSV: {path}')

    def load_json_prompt(self) -> None:
        path = filedialog.askopenfilename(filetypes=[('JSON files', '*.json')])
        if not path:
            return
        try:
            raw = json.loads(Path(path).read_text(encoding='utf-8'))
            self.leads = [Lead(**item) for item in raw]
            self.save_data()
            self.refresh_table()
            self.set_status(f'Imported JSON: {path}')
        except Exception as e:
            messagebox.showerror('Import Error', f'Could not import JSON: {e}')

    def show_data_path(self) -> None:
        messagebox.showinfo('Data File', f'Local auto-save file:\n{self.data_path.resolve()}')


def main() -> None:
    root = tk.Tk()
    app = PipelineApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()
