import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import os
import json

DATA_FILE = "ai_studio_data.json"

CATEGORY_RULES = {
    "Android / Mobile (Kotlin/Java)": ["android", "java", "swift", "deepseek-coder-v2"],
    "Web Development (HTML/CSS/JS)": ["web", "html", "javascript", "react", "starcoder"],
    "Python / Data Science": ["python", "codellama"],
    "Reasoning / Complex Logic": ["deepseek-r1", "qwq", "reasoning", "llama3.3", "llama3.1", "phi4"],
    "General Coding / Multi-language": ["coder", "phind", "wizard"],
    "General Chat & Text": ["llama", "mistral", "gemma", "phi", "qwen", "deepseek"]
}

GITIGNORE_TEMPLATES = {
    "Python": "__pycache__/\n*.py[cod]\n*$py.class\nvenv/\n.venv/\nenv/\n.env\n.idea/\n.vscode/",
    "Android / Java": "*.iml\n.gradle\n/local.properties\n/.idea/\n.DS_Store\n/build\n/captures\n.externalNativeBuild\n.cxx\napp/build/",
    "Web (Node/JS)": "node_modules/\n.env\nbuild/\ndist/\n.DS_Store\n.vscode/",
    "Generic / Other": ".idea/\n.vscode/\n.DS_Store"
}

CLOUD_MODELS = {
    "Cloud AI (Google Gemini)": [
        "gemini/gemini-1.5-pro-latest",
        "gemini/gemini-1.5-flash",
        "gemini/gemini-2.0-flash-exp"
    ],
    "Cloud AI (Groq)": [
        "groq/llama-3.3-70b-versatile",
        "groq/llama-3.1-8b-instant",
        "groq/mixtral-8x7b-32768"
    ]
}

LANGUAGES = {
    "EN": {
        "title": "AI Coder Studio (Hybrid v8)",
        "tab_new": "New Project",
        "tab_fav": "Favorites",
        "tab_hist": "History",
        "cat_lbl": "1. Project Category:",
        "mod_lbl": "2. Select AI Model (Architect):",
        "api_gemini": "Gemini API Key:",
        "api_groq": "Groq API Key:",
        "chk_arch": "Enable Architect Mode",
        "editor_lbl": "Select AI Editor (Local Only):",
        "fld_lbl": "3. Project Folder:",
        "btn_browse": "Browse...",
        "git_lbl": "4. Setup Repo Map:",
        "btn_git": "Initialize Git Map",
        "btn_reload": "Reload Models",
        "fav_chk": "Save to Favorites as:",
        "btn_launch": "LAUNCH AIDER",
        "btn_launch_sel": "Launch Selected",
        "btn_delete": "Delete",
        "btn_launch_hist": "Launch from History",
        "err_title": "Error",
        "warn_ollama": "Ollama is not running! Local models are hidden.",
        "warn_api": "Please enter the required API Key for Cloud models!",
        "err_folder": "Select a folder first!",
        "git_success": "Git Repo created!",
        "lang_btn": "EL"
    },
    "GR": {
        "title": "AI Coder Studio (Υβριδική v8)",
        "tab_new": "Νέο Project",
        "tab_fav": "Αγαπημένα",
        "tab_hist": "Ιστορικό",
        "cat_lbl": "1. Κατηγορία Project:",
        "mod_lbl": "2. Επιλογή Μοντέλου AI (Αρχιτέκτονας):",
        "api_gemini": "Gemini API Key:",
        "api_groq": "Groq API Key:",
        "chk_arch": "Ενεργοποίηση Architect Mode",
        "editor_lbl": "Επιλογή AI Εργάτη (Μόνο Τοπικά):",
        "fld_lbl": "3. Φάκελος Project:",
        "btn_browse": "Αναζήτηση...",
        "git_lbl": "4. Ρύθμιση Repo Map:",
        "btn_git": "Δημιουργία Git Map",
        "btn_reload": "Ανανέωση Μοντέλων",
        "fav_chk": "Αποθήκευση στα Αγαπημένα ως:",
        "btn_launch": "ΕΚΚΙΝΗΣΗ AIDER",
        "btn_launch_sel": "Εκκίνηση Επιλεγμένου",
        "btn_delete": "Διαγραφή",
        "btn_launch_hist": "Εκκίνηση από Ιστορικό",
        "err_title": "Σφάλμα",
        "warn_ollama": "Το Ollama είναι κλειστό! Τα τοπικά μοντέλα κρύφτηκαν.",
        "warn_api": "Εισάγετε το API Key για τα Cloud μοντέλα!",
        "err_folder": "Επιλέξτε φάκελο!",
        "git_success": "Το Git Repository δημιουργήθηκε!",
        "lang_btn": "EN"
    }
}

class AIStudioApp:
    def __init__(self, root):
        self.root = root
        self.root.geometry("650x780")
        self.root.resizable(False, False)

        self.data = self.load_data()
        self.lang = self.data.get("language", "EN")
        
        self.models_dict, self.all_models_flat = self.scan_and_categorize(silent=True)

        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(expand=True, fill='both')

        self.build_ui()
        self.check_ollama_status()

    def check_ollama_status(self):
        try:
            subprocess.run(['ollama', 'list'], capture_output=True, text=True, check=True, timeout=2)
        except:
            messagebox.showwarning("System Info", self.t("warn_ollama"))

    def t(self, key):
        return LANGUAGES[self.lang][key]

    def load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except: pass
        return {"favorites": [], "history": [], "language": "EN", "gemini_api_key": "", "groq_api_key": ""}

    def save_data(self):
        self.data["language"] = self.lang
        if hasattr(self, 'gemini_api_var'): self.data["gemini_api_key"] = self.gemini_api_var.get().strip()
        if hasattr(self, 'groq_api_var'): self.data["groq_api_key"] = self.groq_api_var.get().strip()
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)

    def scan_and_categorize(self, silent=False):
        models = []
        categorized = {**CLOUD_MODELS, **{cat: [] for cat in CATEGORY_RULES.keys()}}
        other_key = "Other Models"
        categorized[other_key] = []
        
        for m_list in CLOUD_MODELS.values(): models.extend(m_list)

        try:
            result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, check=True, timeout=3)
            lines = result.stdout.strip().split('\n')[1:]
            ollama_models = [line.split()[0] for line in lines if line.strip()]
            models.extend(ollama_models)
            
            for model in ollama_models:
                matched = False
                for cat, keywords in CATEGORY_RULES.items():
                    if any(kw in model.lower() for kw in keywords):
                        categorized[cat].append(model)
                        matched = True; break
                if not matched: categorized[other_key].append(model)
        except:
            pass

        return {k: v for k, v in categorized.items() if v}, models

    def reload_app_models(self):
        self.save_data()
        self.models_dict, self.all_models_flat = self.scan_and_categorize()
        self.cat_combo['values'] = list(self.models_dict.keys())
        local_editors = [m for m in self.all_models_flat if not any(x in m for x in ["gemini/", "groq/"])]
        self.editor_combo['values'] = local_editors
        if self.models_dict:
            self.cat_combo.current(0)
            self.update_models_dropdown()
        messagebox.showinfo("Success", "Models updated!")

    def toggle_language(self):
        self.lang = "GR" if self.lang == "EN" else "EN"
        self.save_data()
        self.models_dict, self.all_models_flat = self.scan_and_categorize(silent=True)
        for widget in self.main_container.winfo_children(): widget.destroy()
        self.build_ui()

    def add_context_menu(self, widget):
        """Προσθέτει δεξί κλικ μενού (Αντιγραφή, Επικόλληση, Αποκοπή) στο widget."""
        menu = tk.Menu(widget, tearoff=0)
        menu.add_command(label="Copy", command=lambda: widget.event_generate("<<Copy>>"))
        menu.add_command(label="Paste", command=lambda: widget.event_generate("<<Paste>>"))
        menu.add_command(label="Cut", command=lambda: widget.event_generate("<<Cut>>"))

        def show_menu(event):
            menu.tk_popup(event.x_root, event.y_root)

        widget.bind("<Button-3>", show_menu)

    def build_ui(self):
        self.root.title(self.t("title"))
        top_bar = ttk.Frame(self.main_container); top_bar.pack(fill='x', padx=10, pady=5)
        ttk.Button(top_bar, text=self.t("lang_btn"), width=6, command=self.toggle_language).pack(side='right')
        ttk.Button(top_bar, text=self.t("btn_reload"), command=self.reload_app_models).pack(side='left')

        self.notebook = ttk.Notebook(self.main_container); self.notebook.pack(expand=True, fill='both', padx=10, pady=(0, 10))
        
        tab_launcher = ttk.Frame(self.notebook); self.notebook.add(tab_launcher, text=self.t("tab_new"))
        self.setup_launcher_tab(tab_launcher)
        
        tab_favs = ttk.Frame(self.notebook); self.notebook.add(tab_favs, text=self.t("tab_fav"))
        self.setup_favorites_tab(tab_favs)
        
        # Προσθήκη History Tab
        tab_history = ttk.Frame(self.notebook); self.notebook.add(tab_history, text=self.t("tab_hist"))
        self.setup_history_tab(tab_history)

    def setup_launcher_tab(self, frame):
        ttk.Label(frame, text=self.t("cat_lbl"), font=('', 10, 'bold')).pack(anchor='w', pady=(10, 2), padx=10)
        self.cat_var = tk.StringVar()
        self.cat_combo = ttk.Combobox(frame, textvariable=self.cat_var, state="readonly", width=55)
        self.cat_combo['values'] = list(self.models_dict.keys()); self.cat_combo.pack(padx=10)
        
        ttk.Label(frame, text=self.t("mod_lbl"), font=('', 10, 'bold')).pack(anchor='w', pady=(10, 2), padx=10)
        self.model_var = tk.StringVar(); self.model_combo = ttk.Combobox(frame, textvariable=self.model_var, state="readonly", width=55); self.model_combo.pack(padx=10)

        # API KEYS με Δεξί Κλικ
        api_frame = ttk.LabelFrame(frame, text="Cloud API Credentials"); api_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(api_frame, text=self.t("api_gemini")).grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.gemini_api_var = tk.StringVar(value=self.data.get("gemini_api_key", ""))
        gemini_entry = ttk.Entry(api_frame, textvariable=self.gemini_api_var, width=35, show="*")
        gemini_entry.grid(row=0, column=1, padx=5, pady=5)
        self.add_context_menu(gemini_entry)
        
        ttk.Label(api_frame, text=self.t("api_groq")).grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.groq_api_var = tk.StringVar(value=self.data.get("groq_api_key", ""))
        groq_entry = ttk.Entry(api_frame, textvariable=self.groq_api_var, width=35, show="*")
        groq_entry.grid(row=1, column=1, padx=5, pady=5)
        self.add_context_menu(groq_entry)

        arch_frame = ttk.LabelFrame(frame, text="Dual AI Mode"); arch_frame.pack(fill='x', padx=10, pady=10)
        self.arch_var = tk.BooleanVar()
        ttk.Checkbutton(arch_frame, text=self.t("chk_arch"), variable=self.arch_var, command=self.toggle_architect_ui).pack(anchor='w', padx=5, pady=5)
        self.editor_lbl = ttk.Label(arch_frame, text=self.t("editor_lbl"))
        self.editor_var = tk.StringVar(); self.editor_combo = ttk.Combobox(arch_frame, textvariable=self.editor_var, state="readonly", width=52)
        local_editors = [m for m in self.all_models_flat if not any(x in m for x in ["gemini/", "groq/"])]
        self.editor_combo['values'] = local_editors
        if local_editors: self.editor_combo.current(0)

        ttk.Label(frame, text=self.t("fld_lbl"), font=('', 10, 'bold')).pack(anchor='w', pady=(10, 2), padx=10)
        path_frame = ttk.Frame(frame); path_frame.pack(fill='x', padx=10)
        self.path_var = tk.StringVar()
        path_entry = ttk.Entry(path_frame, textvariable=self.path_var, width=40)
        path_entry.pack(side='left', expand=True, fill='x', padx=(0, 5))
        self.add_context_menu(path_entry)
        ttk.Button(path_frame, text=self.t("btn_browse"), command=self.browse_folder).pack(side='right')

        git_frame = ttk.Frame(frame); git_frame.pack(fill='x', padx=10, pady=(15, 0))
        ttk.Label(git_frame, text=self.t("git_lbl"), font=('', 10, 'bold')).pack(anchor='w', pady=(0, 2))
        git_controls = ttk.Frame(git_frame); git_controls.pack(fill='x')
        self.git_template_var = tk.StringVar(); self.git_template_combo = ttk.Combobox(git_controls, textvariable=self.git_template_var, state="readonly", width=25)
        self.git_template_combo['values'] = list(GITIGNORE_TEMPLATES.keys()); self.git_template_combo.pack(side='left', padx=(0, 10))
        ttk.Button(git_controls, text=self.t("btn_git"), command=self.setup_git_repo).pack(side='left')

        # Αγαπημένα
        fav_frame = ttk.Frame(frame); fav_frame.pack(fill='x', padx=10, pady=(15, 0))
        self.save_fav_var = tk.BooleanVar(); ttk.Checkbutton(fav_frame, text=self.t("fav_chk"), variable=self.save_fav_var).pack(side='left')
        self.fav_name_var = tk.StringVar()
        fav_entry = ttk.Entry(fav_frame, textvariable=self.fav_name_var, width=25)
        fav_entry.pack(side='left', padx=5)
        self.add_context_menu(fav_entry)

        ttk.Button(frame, text=self.t("btn_launch"), command=self.launch_from_main).pack(pady=20, ipadx=20, ipady=10)

        self.cat_combo.bind('<<ComboboxSelected>>', self.update_models_dropdown)
        if self.models_dict:
            self.cat_combo.current(0)
            self.update_models_dropdown()

    def toggle_architect_ui(self):
        if self.arch_var.get(): self.editor_lbl.pack(); self.editor_combo.pack()
        else: self.editor_lbl.pack_forget(); self.editor_combo.pack_forget()

    def update_models_dropdown(self, event=None):
        if not hasattr(self, 'cat_combo'): return
        selected_cat = self.cat_var.get(); models = self.models_dict.get(selected_cat, [])
        self.model_combo['values'] = models
        if models: self.model_combo.current(0)
        
        if hasattr(self, 'git_template_combo') and self.git_template_combo.winfo_exists():
            if "Android" in selected_cat: self.git_template_combo.set("Android / Java")
            elif "Python" in selected_cat: self.git_template_combo.set("Python")
            elif "Web" in selected_cat: self.git_template_combo.set("Web (Node/JS)")
            else: self.git_template_combo.set("Generic / Other")

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder: self.path_var.set(folder)

    def setup_git_repo(self):
        p = self.path_var.get()
        if not p or not os.path.exists(p): messagebox.showerror("Error", self.t("err_folder")); return
        try:
            with open(os.path.join(p, ".gitignore"), "w") as f: f.write(GITIGNORE_TEMPLATES.get(self.git_template_var.get(), ""))
            subprocess.run(["git", "init"], cwd=p, capture_output=True)
            subprocess.run(["git", "add", "."], cwd=p, capture_output=True)
            subprocess.run(["git", "commit", "-m", "Auto-commit"], cwd=p, capture_output=True)
            messagebox.showinfo("Success", self.t("git_success"))
        except Exception as e: messagebox.showerror("Error", str(e))

    def setup_favorites_tab(self, frame):
        self.fav_listbox = tk.Listbox(frame, width=70, height=20)
        self.fav_listbox.pack(pady=10, padx=10)
        self.refresh_favorites_list()
        
        btn_frame = ttk.Frame(frame); btn_frame.pack(pady=5)
        ttk.Button(btn_frame, text=self.t("btn_launch_sel"), command=self.launch_favorite).pack(side='left', padx=5)
        ttk.Button(btn_frame, text=self.t("btn_delete"), command=self.delete_favorite).pack(side='left', padx=5)

    def setup_history_tab(self, frame):
        self.hist_listbox = tk.Listbox(frame, width=70, height=20)
        self.hist_listbox.pack(pady=10, padx=10)
        self.refresh_history_list()
        
        ttk.Button(frame, text=self.t("btn_launch_hist"), command=self.launch_history).pack(pady=5)

    def refresh_favorites_list(self):
        self.fav_listbox.delete(0, tk.END)
        for fav in self.data["favorites"]:
            editor_str = f" + {fav.get('editor', '')}" if fav.get('editor') else ""
            self.fav_listbox.insert(tk.END, f"[{fav['name']}] - {fav['model']}{editor_str} ({fav['path']})")

    def refresh_history_list(self):
        self.hist_listbox.delete(0, tk.END)
        for h in reversed(self.data["history"]):
            editor_str = f" + {h.get('editor', '')}" if h.get('editor') else ""
            self.hist_listbox.insert(tk.END, f"{h['model']}{editor_str} -> {h['path']}")

    def launch_aider(self, model, path, editor=None):
        if not path or not os.path.isdir(path): messagebox.showerror("Error", self.t("err_folder")); return
        self.save_data()
        is_gemini, is_groq = model.startswith("gemini/"), model.startswith("groq/")
        env_prefix = ""
        if is_gemini:
            if not self.data["gemini_api_key"]: messagebox.showwarning("API Key", self.t("warn_api")); return
            env_prefix = f'set GEMINI_API_KEY={self.data["gemini_api_key"]}&& '
        if is_groq:
            if not self.data["groq_api_key"]: messagebox.showwarning("API Key", self.t("warn_api")); return
            env_prefix = f'set GROQ_API_KEY={self.data["groq_api_key"]}&& '

        # Αποθήκευση στο History
        hist_entry = {"model": model, "path": path, "editor": editor}
        if hist_entry in self.data["history"]: self.data["history"].remove(hist_entry)
        self.data["history"].append(hist_entry)
        if len(self.data["history"]) > 20: self.data["history"].pop(0)
        self.save_data()
        self.refresh_history_list()

        model_arg = f"--model {model}" if (is_gemini or is_groq) else f"--model ollama/{model}"
        if editor:
            ed_arg = f"--editor-model ollama/{editor}"
            cmd = f'start "Aider" cmd /k "cd /d "{path}" && {env_prefix}aider {model_arg} {ed_arg} --architect --no-show-model-warnings"'
        else:
            cmd = f'start "Aider" cmd /k "cd /d "{path}" && {env_prefix}aider {model_arg} --no-show-model-warnings"'
        os.system(cmd)

    def launch_from_main(self):
        m, p, e = self.model_var.get(), self.path_var.get(), (self.editor_var.get() if self.arch_var.get() else None)
        
        if self.save_fav_var.get():
            name = self.fav_name_var.get().strip()
            if not name: messagebox.showwarning("Warning", "Please provide a name for your Favorite!"); return
            self.data["favorites"].append({"name": name, "model": m, "path": p, "editor": e})
            self.save_data()
            self.refresh_favorites_list()
            self.save_fav_var.set(False)
            self.fav_name_var.set("")
            
        self.launch_aider(m, p, e)

    def launch_favorite(self):
        sel = self.fav_listbox.curselection()
        if sel: 
            fav = self.data["favorites"][sel[0]]
            self.launch_aider(fav['model'], fav['path'], fav.get('editor'))

    def delete_favorite(self):
        sel = self.fav_listbox.curselection()
        if sel: 
            del self.data["favorites"][sel[0]]
            self.save_data()
            self.refresh_favorites_list()

    def launch_history(self):
        sel = self.hist_listbox.curselection()
        if sel:
            # Επειδή η λίστα είναι reversed στο UI, βρίσκουμε το σωστό index
            real_index = len(self.data["history"]) - 1 - sel[0]
            h = self.data["history"][real_index]
            self.launch_aider(h['model'], h['path'], h.get('editor'))

if __name__ == "__main__":
    root = tk.Tk(); app = AIStudioApp(root); root.mainloop()