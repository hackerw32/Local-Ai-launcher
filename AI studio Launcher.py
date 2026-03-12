import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import os
import json

# Αρχείο αποθήκευσης δεδομένων
DATA_FILE = "ai_studio_data.json"

# Κανόνες Κατηγοριοποίησης
CATEGORY_RULES = {
    "Android / Mobile (Kotlin/Java)": ["android", "java", "swift", "deepseek-coder"],
    "Web Development (HTML/CSS/JS)": ["web", "html", "javascript", "react", "starcoder"],
    "Python / Data Science": ["python", "codellama","phi"],
    "Reasoning / Complex Logic": ["deepseek-r1", "qwq", "reasoning", "llama3"],
    "General Coding / Multi-language": ["coder", "qwen2.5-coder", "phind"],
    "General Chat & Text": ["llama", "mistral", "gemma"]
}

# Σύστημα Μεταφράσεων
LANGUAGES = {
    "EN": {
        "title": "AI Coder Studio (Local Ollama)",
        "tab_new": "New Project",
        "tab_fav": "Favorites",
        "tab_hist": "History",
        "cat_lbl": "1. Project Category:",
        "mod_lbl": "2. Select AI Model:",
        "fld_lbl": "3. Project Folder:",
        "btn_browse": "Browse...",
        "fav_chk": "Save to Favorites as:",
        "btn_launch": "LAUNCH AIDER",
        "btn_launch_sel": "Launch Selected",
        "btn_delete": "Delete",
        "btn_launch_hist": "Launch from History",
        "err_title": "Error",
        "err_ollama": "Ollama was not found or is not running!",
        "err_folder": "Please select a valid folder!",
        "warn_title": "Warning",
        "warn_fav": "Please provide a name for your Favorite!",
        "other_models": "Other Models",
        "lang_btn": "🇬🇷 ΕΛ"
    },
    "GR": {
        "title": "AI Coder Studio (Τοπικό Ollama)",
        "tab_new": "Νέο Project",
        "tab_fav": "Αγαπημένα",
        "tab_hist": "Ιστορικό",
        "cat_lbl": "1. Κατηγορία Project:",
        "mod_lbl": "2. Επιλογή Μοντέλου AI:",
        "fld_lbl": "3. Φάκελος Project:",
        "btn_browse": "Αναζήτηση...",
        "fav_chk": "Αποθήκευση στα Αγαπημένα ως:",
        "btn_launch": "ΕΚΚΙΝΗΣΗ AIDER",
        "btn_launch_sel": "Εκκίνηση Επιλεγμένου",
        "btn_delete": "Διαγραφή",
        "btn_launch_hist": "Εκκίνηση από Ιστορικό",
        "err_title": "Σφάλμα",
        "err_ollama": "Το Ollama δεν βρέθηκε ή δεν τρέχει!",
        "err_folder": "Παρακαλώ επέλεξε έναν έγκυρο φάκελο!",
        "warn_title": "Προσοχή",
        "warn_fav": "Δώσε όνομα για το Αγαπημένο σου!",
        "other_models": "Άλλα Μοντέλα",
        "lang_btn": "🇬🇧 EN"
    }
}

class AIStudioApp:
    def __init__(self, root):
        self.root = root
        self.root.geometry("600x470")
        self.root.resizable(False, False)

        # Φόρτωση δεδομένων (Ιστορικό, Αγαπημένα, Γλώσσα)
        self.data = self.load_data()
        self.lang = self.data.get("language", "EN") # Default English
        
        self.models_dict = self.scan_and_categorize()

        # Κεντρικό Frame που θα φιλοξενεί τα πάντα
        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(expand=True, fill='both')

        self.build_ui()

    def t(self, key):
        """Επιστρέφει το κείμενο στη σωστή γλώσσα"""
        return LANGUAGES[self.lang][key]

    def load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {"favorites": [], "history": [], "language": "EN"}

    def save_data(self):
        self.data["language"] = self.lang
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)

    def scan_and_categorize(self):
        try:
            result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, check=True)
            lines = result.stdout.strip().split('\n')[1:]
            models = [line.split()[0] for line in lines if line.strip()]
        except Exception:
            messagebox.showerror(self.t("err_title"), self.t("err_ollama"))
            return {"Error": ["No models found"]}

        categorized = {cat: [] for cat in CATEGORY_RULES.keys()}
        other_key = self.t("other_models")
        categorized[other_key] = []

        for model in models:
            matched = False
            for cat, keywords in CATEGORY_RULES.items():
                if any(kw in model.lower() for kw in keywords):
                    categorized[cat].append(model)
                    matched = True
                    break
            if not matched:
                categorized[other_key].append(model)
                
        return {k: v for k, v in categorized.items() if v}

    def toggle_language(self):
        # Αλλαγή γλώσσας
        self.lang = "GR" if self.lang == "EN" else "EN"
        self.save_data()
        
        # Ξανασκανάρισμα για να αλλάξει το όνομα του "Other Models"
        self.models_dict = self.scan_and_categorize()

        # Καθαρισμός και επανασχεδιασμός του UI
        for widget in self.main_container.winfo_children():
            widget.destroy()
        self.build_ui()

    def build_ui(self):
        self.root.title(self.t("title"))

        # Top Bar (για το κουμπί γλώσσας)
        top_bar = ttk.Frame(self.main_container)
        top_bar.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(top_bar, text=self.t("lang_btn"), width=6, command=self.toggle_language).pack(side='right')

        # Δημιουργία Tabs (Notebook)
        self.notebook = ttk.Notebook(self.main_container)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=(0, 10))

        # Tab 1: Launcher
        tab_launcher = ttk.Frame(self.notebook)
        self.notebook.add(tab_launcher, text=self.t("tab_new"))
        self.setup_launcher_tab(tab_launcher)

        # Tab 2: Favorites
        tab_favs = ttk.Frame(self.notebook)
        self.notebook.add(tab_favs, text=self.t("tab_fav"))
        self.setup_favorites_tab(tab_favs)

        # Tab 3: History
        tab_history = ttk.Frame(self.notebook)
        self.notebook.add(tab_history, text=self.t("tab_hist"))
        self.setup_history_tab(tab_history)

    def setup_launcher_tab(self, frame):
        # Επιλογή Κατηγορίας
        ttk.Label(frame, text=self.t("cat_lbl"), font=('', 10, 'bold')).pack(anchor='w', pady=(10, 2), padx=10)
        self.cat_var = tk.StringVar()
        self.cat_combo = ttk.Combobox(frame, textvariable=self.cat_var, state="readonly", width=50)
        self.cat_combo['values'] = list(self.models_dict.keys())
        self.cat_combo.pack(padx=10)
        self.cat_combo.bind('<<ComboboxSelected>>', self.update_models_dropdown)

        # Επιλογή Μοντέλου
        ttk.Label(frame, text=self.t("mod_lbl"), font=('', 10, 'bold')).pack(anchor='w', pady=(15, 2), padx=10)
        self.model_var = tk.StringVar()
        self.model_combo = ttk.Combobox(frame, textvariable=self.model_var, state="readonly", width=50)
        self.model_combo.pack(padx=10)

        if self.models_dict:
            self.cat_combo.current(0)
            self.update_models_dropdown()

        # Επιλογή Φακέλου
        ttk.Label(frame, text=self.t("fld_lbl"), font=('', 10, 'bold')).pack(anchor='w', pady=(15, 2), padx=10)
        path_frame = ttk.Frame(frame)
        path_frame.pack(fill='x', padx=10)
        
        self.path_var = tk.StringVar()
        path_entry = ttk.Entry(path_frame, textvariable=self.path_var, width=40)
        path_entry.pack(side='left', expand=True, fill='x', padx=(0, 5))
        ttk.Button(path_frame, text=self.t("btn_browse"), command=self.browse_folder).pack(side='right')

        # Αποθήκευση στα Αγαπημένα
        self.save_fav_var = tk.BooleanVar()
        fav_frame = ttk.Frame(frame)
        fav_frame.pack(fill='x', padx=10, pady=(20, 0))
        ttk.Checkbutton(fav_frame, text=self.t("fav_chk"), variable=self.save_fav_var).pack(side='left')
        self.fav_name_var = tk.StringVar()
        ttk.Entry(fav_frame, textvariable=self.fav_name_var, width=25).pack(side='left', padx=5)

        # Κουμπί Εκκίνησης
        ttk.Button(frame, text=self.t("btn_launch"), command=self.launch_from_main).pack(pady=20, ipadx=20, ipady=10)

    def update_models_dropdown(self, event=None):
        selected_cat = self.cat_var.get()
        models = self.models_dict.get(selected_cat, [])
        self.model_combo['values'] = models
        if models:
            self.model_combo.current(0)

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.path_var.set(folder)

    def setup_favorites_tab(self, frame):
        self.fav_listbox = tk.Listbox(frame, width=70, height=15)
        self.fav_listbox.pack(pady=10, padx=10)
        self.refresh_favorites_list()

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=5)
        ttk.Button(btn_frame, text=self.t("btn_launch_sel"), command=self.launch_favorite).pack(side='left', padx=5)
        ttk.Button(btn_frame, text=self.t("btn_delete"), command=self.delete_favorite).pack(side='left', padx=5)

    def setup_history_tab(self, frame):
        self.hist_listbox = tk.Listbox(frame, width=70, height=15)
        self.hist_listbox.pack(pady=10, padx=10)
        self.refresh_history_list()

        ttk.Button(frame, text=self.t("btn_launch_hist"), command=self.launch_history).pack(pady=5)

    def refresh_favorites_list(self):
        self.fav_listbox.delete(0, tk.END)
        for fav in self.data["favorites"]:
            self.fav_listbox.insert(tk.END, f"[{fav['name']}]  -  {fav['model']}  ({fav['path']})")

    def refresh_history_list(self):
        self.hist_listbox.delete(0, tk.END)
        for h in reversed(self.data["history"]):
            self.hist_listbox.insert(tk.END, f"{h['model']}  ->  {h['path']}")

    def launch_aider(self, model, path):
        if not path or not os.path.isdir(path):
            messagebox.showerror(self.t("err_title"), self.t("err_folder"))
            return

        hist_entry = {"model": model, "path": path}
        if hist_entry in self.data["history"]:
            self.data["history"].remove(hist_entry)
        self.data["history"].append(hist_entry)
        if len(self.data["history"]) > 20:
            self.data["history"].pop(0)
        
        self.save_data()
        self.refresh_history_list()

        cmd_command = f'start "Aider: {model}" cmd /k "cd /d "{path}" && aider --model ollama/{model} --no-show-model-warnings"'
        os.system(cmd_command)

    def launch_from_main(self):
        model = self.model_var.get()
        path = self.path_var.get()
        
        if self.save_fav_var.get():
            fav_name = self.fav_name_var.get().strip()
            if not fav_name:
                messagebox.showwarning(self.t("warn_title"), self.t("warn_fav"))
                return
            self.data["favorites"].append({"name": fav_name, "model": model, "path": path})
            self.save_data()
            self.refresh_favorites_list()
            self.save_fav_var.set(False)
            self.fav_name_var.set("")

        self.launch_aider(model, path)

    def launch_favorite(self):
        sel = self.fav_listbox.curselection()
        if sel:
            fav = self.data["favorites"][sel[0]]
            self.launch_aider(fav['model'], fav['path'])

    def delete_favorite(self):
        sel = self.fav_listbox.curselection()
        if sel:
            del self.data["favorites"][sel[0]]
            self.save_data()
            self.refresh_favorites_list()

    def launch_history(self):
        sel = self.hist_listbox.curselection()
        if sel:
            real_index = len(self.data["history"]) - 1 - sel[0]
            h = self.data["history"][real_index]
            self.launch_aider(h['model'], h['path'])

if __name__ == "__main__":
    root = tk.Tk()
    app = AIStudioApp(root)
    root.mainloop()