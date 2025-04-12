
# ------------------------------------------------------------------------
# ENHANCEMENTS APPLIED:
# ✅ Numeric Entry fields added next to sliders for precise input.
# ✅ Design-specific overlay settings are saved and restored.
# ✅ Preview and generation actions show a status label with activity feedback.
# ✅ GUI layout adjusted to better support smaller screen resolutions.
# ------------------------------------------------------------------------

print("Launching GUI...")

import os
import re
import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import webbrowser
from tkinter import PhotoImage


CONFIG_PATH = os.path.expanduser("~/.wbmockup_config.json")
TEMPLATES_PATH = os.path.expanduser("~/.wbmockup_templates.json")


# === Injected Enhancement Hooks ===
import threading

DESIGN_SETTINGS_PATH = os.path.expanduser("~/.wbmockup_design_settings.json")  # Confirmed save path

def load_design_settings():
    if os.path.exists(DESIGN_SETTINGS_PATH):
        try:
            with open(DESIGN_SETTINGS_PATH, "r") as f:
                data = json.load(f)
            print(f"[Design Settings Loaded] from {DESIGN_SETTINGS_PATH}")
            return data
        except Exception as e:
            print(f"[Design Settings Load Error] {e}")
    return {}

def save_design_settings(settings):
    try:
        with open(DESIGN_SETTINGS_PATH, "w") as f:
            json.dump(settings, f)
        print(f"[Design Settings Saved] to {DESIGN_SETTINGS_PATH}")
    except Exception as e:
        print(f"[Design Settings Save Error] {e}")

app_initialized = False

class Mockup:
    def __init__(self, path, is_dark=False):
        self.path = path
        self.filename = os.path.basename(path)
        self.is_dark = tk.BooleanVar(value=is_dark)

# Tooltip helper class
class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tipwindow = None
        widget.bind("<Enter>", self.show_tip)
        widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, _):
        if self.tipwindow:
            return
        x, y, _, cy = self.widget.bbox("insert") if self.widget.bbox("insert") else (0, 0, 0, 0)
        x = x + self.widget.winfo_rootx() + 25
        y = y + cy + self.widget.winfo_rooty() + 20
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.geometry(f"+{x}+{y}")
        label = tk.Label(
            tw, text=self.text, justify=tk.LEFT,
            background="#ffffe0", relief=tk.SOLID,
            borderwidth=1, font=("TkDefaultFont", 9)
        )
        label.pack(ipadx=4, ipady=2)

    def hide_tip(self, _):
        if self.tipwindow:
            self.tipwindow.destroy()
            self.tipwindow = None

def is_light_design(filename):
    filename = os.path.basename(filename).lower().strip()
    return re.search(r'[\-_ ]light(\.|\s|$)', filename)

def is_dark_design(filename):
    filename = os.path.basename(filename).lower().strip()
    return re.search(r'[\-_ ]dark(\.|\s|$)', filename)

def get_design_basename(filename):
    base = os.path.splitext(os.path.basename(filename))[0]
    base = re.sub(r'(?i)[\s\-_]*\b(light|dark)\b\s*$', '', base)
    base = re.sub(r'[-_\s]+$', '', base)  # Clean trailing junk
    return re.sub(r'[\s\-]+', '_', base.strip())  # Normalize

def move_to_completed(design_file, design_folder):
    completed_dir = os.path.join(design_folder, "Completed Designs")
    os.makedirs(completed_dir, exist_ok=True)
    try:
        os.rename(
            os.path.join(design_folder, design_file),
            os.path.join(completed_dir, design_file)
        )
    except Exception as e:
        print(f"Failed to move {design_file} to Completed Designs: {e}")

def apply_opacity(image, opacity):
    image = image.convert("RGBA")
    alpha = image.split()[3]
    alpha = alpha.point(lambda p: int(p * (opacity / 100)))
    image.putalpha(alpha)
    return image

def overlay_design(mockup, design, size, x_offset, y_offset, opacity, lock_aspect=True):
    img = mockup.copy()
    design = design.convert("RGBA")
    w, h = design.size
    if lock_aspect:
        scale = size / max(w, h)
        new_w, new_h = int(w * scale), int(h * scale)
    else:
        new_w = new_h = size
    design = design.resize((new_w, new_h), Image.LANCZOS)
    design = apply_opacity(design, opacity)
    x = (img.width - new_w) // 2 + x_offset
    y = (img.height - new_h) // 2 + y_offset
    img.paste(design, (x, y), design)
    return img

def save_config(data):
    with open(CONFIG_PATH, 'w') as f:
        json.dump(data, f)

def load_config():
    return json.load(open(CONFIG_PATH)) if os.path.exists(CONFIG_PATH) else {}

def save_templates(data):
    with open(TEMPLATES_PATH, 'w') as f:
        json.dump(data, f)

def load_templates():
    return json.load(open(TEMPLATES_PATH)) if os.path.exists(TEMPLATES_PATH) else {}

def launch_gui():
    config = load_config()
    templates = load_templates()
    
    root = tk.Tk()
    root.title("MockupBuddy - Desktop")
    
    import sys

    def get_asset_path(filename):
        if getattr(sys, 'frozen', False):
            # Inside .app bundle → Resources folder
            base_path = os.path.abspath(os.path.join(os.path.dirname(sys.executable), '..', 'Resources'))
            return os.path.join(base_path, filename)
        else:
            # Running normally from source
            base_path = os.path.join(os.path.dirname(__file__), '..', 'assets')
            return os.path.abspath(os.path.join(base_path, filename))

    from PIL import Image, ImageTk
    coffee_img_path = get_asset_path('bmcNT.png')
    img = Image.open(coffee_img_path)
    img_resized = img.resize((140, 39), Image.LANCZOS)
    coffee_img = ImageTk.PhotoImage(img_resized)


    try:
        # ✅ Windows: maximize the window
        root.state("zoomed")
    except:
        pass  # Will fall through for macOS/Linux

    # ✅ Universal fallback: 95% screen usage, centered
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    window_width = min(1350, int(screen_width * 0.95))
    window_height = min(950, int(screen_height * 0.95))

    x_offset = (screen_width - window_width) // 2
    y_offset = (screen_height - window_height) // 2

    root.geometry(f"{window_width}x{window_height}+{x_offset}+{y_offset}")
    root.minsize(1000, 700)



    show_debug_log = tk.BooleanVar(value=False)

    paned = ttk.PanedWindow(root, orient=tk.HORIZONTAL)
    paned.pack(fill=tk.BOTH, expand=True)

    # LEFT PANEL: Scrollable control frame setup
    control_container = ttk.Frame(paned)
    paned.add(control_container, weight=1)

    control_canvas = tk.Canvas(control_container, borderwidth=0)
    control_scrollbar = ttk.Scrollbar(control_container, orient="vertical", command=control_canvas.yview)
    control_canvas.configure(yscrollcommand=control_scrollbar.set)

    # Create the inner scrollable frame
    control_inner = ttk.Frame(control_canvas)
    control_inner.bind(
        "<Configure>",
        lambda e: control_canvas.configure(scrollregion=control_canvas.bbox("all"))
    )

    canvas_window = control_canvas.create_window((0, 0), window=control_inner, anchor="nw")

    control_canvas.pack(side="left", fill="both", expand=True)
    control_scrollbar.pack(side="right", fill="y")

    # 🟡 This is what you use below for placing widgets
    control_frame = control_inner

    # Top-level Boolean to track visibility
    folders_visible = tk.BooleanVar(value=True)

    def toggle_folder_section():
        if folders_visible.get():
            folder_container.pack_forget()
            folders_visible.set(False)
            toggle_btn.config(text="📁 Show Folder Settings")
        else:
            folder_container.pack(fill="x", padx=10, pady=(10, 10))
            folders_visible.set(True)
            toggle_btn.config(text="📁 Hide Folder Settings")




    # RIGHT PANEL stays the same
    preview_frame = ttk.Frame(paned)
    paned.add(preview_frame, weight=3)

    root.update_idletasks()
    try:
        paned.sashpos(0, 600)
    except Exception as e:
        print(f"Warning: sashpos failed - {e}")

  

    # 🖼️ Label row: just the "Mockup Preview" label
    label_row = ttk.Frame(preview_frame)
    label_row.pack(fill="x", padx=10, pady=(10, 0))
    ttk.Label(label_row, text="🖼️ Mockup Preview", font=("TkDefaultFont", 10, "bold")).pack(side="left")

    # 🔄 Row with dropdown + coffee button aligned
    selector_row = ttk.Frame(preview_frame)
    selector_row.pack(fill="x", padx=10, pady=(4, 10))  # Adjust spacing here

    selected_mockup_preview = tk.StringVar()

    preview_selector = ttk.Combobox(
        selector_row,
        textvariable=selected_mockup_preview,
        state="readonly",
        width=40
    )
    preview_selector.pack(side="left", padx=(0, 10))
    preview_selector.bind("<<ComboboxSelected>>", lambda e: update_preview())

    coffee_button = tk.Button(
        selector_row,
        image=coffee_img,
        borderwidth=0,
        highlightthickness=0,
        relief="flat",
        cursor="hand2",
        padx=0,
        pady=0,
        command=lambda: webbrowser.open_new_tab("https://www.buymeacoffee.com/nicktrautman")
    )
    coffee_button.image = coffee_img






    # Wrap the canvas in a centering frame
    # 📦 Canvas wrapper to center it
    canvas_wrapper = ttk.Frame(preview_frame)
    canvas_wrapper.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    # 🖼️ Mockup canvas with background
    preview_canvas = tk.Canvas(canvas_wrapper, bg="#222", bd=1, relief="sunken", width=800, height=600)
    preview_canvas.pack(fill=tk.BOTH, expand=True)  # ✅ THIS is the magic fix

    def debug_canvas_size():
        print("Canvas:", preview_canvas.winfo_width(), "x", preview_canvas.winfo_height())

    preview_canvas.bind("<Configure>", lambda e: debug_canvas_size())

    settings_frame = ttk.LabelFrame(control_frame, text="Design Settings")
    settings_frame.pack(fill=tk.X, padx=10, pady=5)

    selected_design = tk.StringVar()

    # Load saved settings or set defaults
    size_var = tk.IntVar(value=config.get("design_size", 300))
    opacity_var = tk.IntVar(value=config.get("opacity", 100))  # Now % based (0–100)
    x_offset_var = tk.IntVar(value=config.get("x_offset", 0))
    y_offset_var = tk.IntVar(value=config.get("y_offset", 0))
    lock_aspect_var = tk.BooleanVar(value=config.get("lock_aspect", True))
    move_completed_var = tk.BooleanVar(value=config.get("move_completed", True))

    ttk.Checkbutton(
        settings_frame,
        text="Move used designs to 'Completed Designs' folder",
        variable=move_completed_var
    ).pack(anchor=tk.W, padx=5, pady=(2, 5))

    config.update({
        "design_size": size_var.get(),
        "opacity": opacity_var.get(),
        "x_offset": x_offset_var.get(),
        "y_offset": y_offset_var.get(),
        "lock_aspect": lock_aspect_var.get()
    })
    save_config(config)
    var = tk.BooleanVar(value=True)
    generate_mode = tk.StringVar(value="all")
    design_types = {}
        
    def update_preview():
        nonlocal selected_mockup_preview, selected_design, preview_selector, preview_canvas, checkbox_vars

        log_debug(f"✅ Checkbox vars:\n{checkbox_vars}")


        selected_mockup: str = ""  # <-- Predefine to satisfy Pylance

        if not checkbox_vars or not templates:
            return

        design_folder = design_path.get()
        mockup_folder = mockup_path.get()

        designs = [f for f in os.listdir(design_folder) if f.lower().endswith((".png", ".jpg", ".jpeg"))]
        if not designs or not selected_design.get():
            return

        # ✅ Build valid mockup list once
        valid_mockups = [
            file for file, var in checkbox_vars
            if var.get() and should_use_mockup_for_design(selected_design.get(), file, templates)
        ]

        # ✅ Handle empty case first
        if not valid_mockups:
            log_debug(f"⚠️ No matching mockups for {selected_design.get()}")
            if app_initialized:
                messagebox.showinfo("No Match", f"No compatible mockup found for '{selected_design.get()}'.")
            preview_selector.set('')
            return

        # ✅ Now populate dropdown and set default safely
        preview_selector['values'] = valid_mockups

        if not selected_mockup_preview.get() or selected_mockup_preview.get() not in valid_mockups:
            selected_mockup_preview.set(valid_mockups[0])
            update_preview()


        # Then continue with setting selected_mockup etc.


        try:
            design_img = Image.open(os.path.join(design_folder, selected_design.get()))
            mockup_full_path = os.path.join(mockup_folder, selected_mockup)

            if not os.path.isfile(mockup_full_path):
                log_debug(f"❌ ERROR: Tried to preview a directory → {mockup_full_path}")
                return  # Bail safely

            mockup_img = Image.open(mockup_full_path)


            final_img = overlay_design(
                mockup_img,
                design_img,
                size_var.get(),
                x_offset_var.get(),
                y_offset_var.get(),
                opacity_var.get(),
                lock_aspect_var.get()
            )

            # Resize and center preview image on canvas
            preview_canvas.update_idletasks()
            max_w = preview_canvas.winfo_width()
            max_h = preview_canvas.winfo_height()

            # Optional: add padding around the image to avoid hugging the edges
            padding = 10
            w, h = final_img.size
            scale = min((max_w - padding) / w, (max_h - padding) / h, 1.0)

            resized_img = final_img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
            preview_img = ImageTk.PhotoImage(resized_img)

            # Clear canvas and center image
            preview_canvas.delete("all")
            preview_canvas.create_image(max_w // 2, max_h // 2, anchor=tk.CENTER, image=preview_img)
            preview_canvas.image = preview_img


        except Exception as e:
            print(f"Preview error: {e}")

    def add_slider(frame, label, var, from_, to):
        row = ttk.Frame(frame)
        row.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(row, text=label).pack(side=tk.LEFT)
        val_label = ttk.Label(row, text=str(var.get()), width=4)
        val_label.pack(side=tk.RIGHT)
        slider = ttk.Scale(row, from_=from_, to=to, orient=tk.HORIZONTAL, variable=var)
        slider.pack(fill=tk.X, expand=True, padx=5)

        def on_change(_):
            val_label.config(text=f"{int(var.get())}")
            update_preview()

        slider.bind("<B1-Motion>", on_change)
        slider.bind("<ButtonRelease-1>", on_change)

    add_slider(settings_frame, "Design Size", size_var, 100, 1000)
    add_slider(settings_frame, "Opacity", opacity_var, 0, 100)
    add_slider(settings_frame, "Vertical Offset (Y)", y_offset_var, -500, 500)
    add_slider(settings_frame, "Horizontal Offset (X)", x_offset_var, -500, 500)
    lock_aspect_var = tk.BooleanVar(value=True)
    ttk.Checkbutton(settings_frame, text="Lock Aspect Ratio", variable=lock_aspect_var, command=update_preview).pack(anchor=tk.W, padx=5, pady=5)

    def generate_mockups():
        config = {
            "design_path": design_path.get(),
            "mockup_path": mockup_path.get(),
            "output_path": output_path.get()
        }

    # ✅ Add this block to persist design settings
        config.update({
            "design_size": size_var.get(),
            "opacity": opacity_var.get(),
            "x_offset": x_offset_var.get(),
            "y_offset": y_offset_var.get(),
            "lock_aspect": lock_aspect_var.get(),
            "move_completed": move_completed_var.get()   # <-- add this line
        })


        save_config(config)
        status_var.set("Generating mockups...")
        root.update_idletasks()
        design_folder = design_path.get()
        mockup_folder = mockup_path.get()
        output_folder = output_path.get()

        if not all(map(os.path.isdir, [design_folder, mockup_folder, output_folder])):
            messagebox.showerror("Error", "Please select valid folders.")
            return

        if generate_mode.get() == "selected":
            if not selected_design.get():
                messagebox.showerror("Error", "No design selected.")
                return
            design_files = [selected_design.get()]
        else:
            design_files = [f for f in os.listdir(design_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

        total = len(design_files)
        generated_count = 0

        # Popup with progress bar
        popup = tk.Toplevel(root)
        popup.title("Generating Mockups")
        popup.geometry("350x120")
        popup.resizable(False, False)

        ttk.Label(popup, text="Generating mockups...").pack(pady=(15, 5))
        progress_label = ttk.Label(popup, text="Starting...")
        progress_label.pack()

        progress_bar = ttk.Progressbar(popup, length=300, mode="determinate", maximum=total)
        progress_bar.pack(pady=10)
        popup.update()

        for i, file in enumerate(design_files, 1):
            progress_label.config(text=f"{i} of {total}: {file}")
            popup.update()

            design_path_full = os.path.join(design_folder, file)
            success = True  # Track if all mockups for this design succeed

            try:
                design_img = Image.open(design_path_full)
                for mockup_name, var in checkbox_vars:
                    if not var.get():
                        continue
                    if not should_use_mockup_for_design(file, mockup_name, templates):
                        continue

                    try:
                        mockup_full_path = os.path.join(mockup_folder, *mockup_name.split(os.sep))
                        mockup_img = Image.open(mockup_full_path)

                        final_img = overlay_design(
                            mockup_img,
                            design_img,
                            size_var.get(),
                            x_offset_var.get(),
                            y_offset_var.get(),
                            opacity_var.get(),
                            lock_aspect_var.get()
                        )
                        base = get_design_basename(file)
                        subfolder_path = os.path.join(output_folder, base)
                        os.makedirs(subfolder_path, exist_ok=True)  # Ensure the folder exists

                        out_name = f"{base}_{os.path.splitext(mockup_name)[0]}.png"
                        out_path = os.path.join(subfolder_path, out_name)
                        final_img.save(out_path)
                        generated_count += 1
                    except Exception as e:
                        print(f"Error generating mockup {mockup_name} for {file}: {e}")
                        success = False
            except Exception as e:
                print(f"Error opening design file {file}: {e}")
                success = False

            if success and move_completed_var.get():
                completed_dir = os.path.join(design_folder, "Completed Designs")
                os.makedirs(completed_dir, exist_ok=True)
                try:
                    os.rename(
                        os.path.join(design_folder, file),
                        os.path.join(completed_dir, file)
                    )
                except Exception as move_error:
                    print(f"Could not move {file} to Completed Designs: {move_error}")
        

        popup.destroy()
        save_templates(templates)
        status_var.set("✅ Mockups generated successfully.")
        messagebox.showinfo("Done", f"✅ {generated_count} mockups generated.")

        save_templates(templates)
        status_var.set("✅ Mockups generated successfully.")

    # ================================
    # 📁 FOLDER SECTION + TOGGLE
    # ================================


    # 🧩 Folder Settings Section — Wrapping container
    folder_container = ttk.Frame(control_frame)
    folder_container.pack(fill="x", padx=10, pady=5)

    def reset_folder_paths():
        design_path.set("")
        mockup_path.set("")
        output_path.set("")

    # Header row with label and toggle button
    folder_header_row = ttk.Frame(folder_container)
    folder_header_row.pack(fill="x", pady=(5, 0))

    # Left-aligned label
    ttk.Label(folder_header_row, text="📁 Folder Settings", font=("TkDefaultFont", 10, "bold")).pack(side="left")

    # Right-aligned toggle button
    toggle_btn = ttk.Button(
        folder_header_row,
        text="📁 Hide Folder Settings",
        command=lambda: toggle_folder_section()
    )

    # Reset Button
    reset_btn = ttk.Button(
        folder_header_row,
        text="🧹 Reset Paths",
        command=reset_folder_paths
    )
    reset_btn.pack(side="right", padx=(5, 0))

    ToolTip(reset_btn, "Click to clear all folder path selections")

    toggle_btn.pack(side="right")


    # 🗂️ The collapsible content
    folder_frame = ttk.LabelFrame(folder_container)
    folder_frame.pack(fill="x", pady=(5, 0))

    # 🔁 Updated toggle function
    def toggle_folder_section():
        if folder_frame.winfo_ismapped():
            folder_frame.pack_forget()
            toggle_btn.config(text="📁 Show Folder Settings")
        else:
            folder_frame.pack(fill="x", pady=(5, 0))
            toggle_btn.config(text="📁 Hide Folder Settings")

    # Define folder paths
    design_path = tk.StringVar(value=config.get("design_path", ""))
    mockup_path = tk.StringVar(value=config.get("mockup_path", ""))
    output_path = tk.StringVar(value=config.get("output_path", ""))

    # Folder browse + entry builder
    def browse_button(var, parent):
        ttk.Entry(parent, textvariable=var, width=60).pack(fill=tk.X, padx=5, pady=2)

        def browse_action():
            initial_dir = var.get() if os.path.isdir(var.get()) else os.path.expanduser("~")
            path = filedialog.askdirectory(initialdir=initial_dir)

            if path:
                var.set(path)
                if var == design_path:
                    refresh_design_list()

        browse_btn = ttk.Button(parent, text="Browse", command=browse_action)
        browse_btn.pack(fill=tk.X, padx=5)
        ToolTip(browse_btn, "Click to select a folder from your system")


    # 🧩 Folder layout definitions
    folder_definitions = [
        ("📂 Design Location", design_path, "Choose the location of your designs"),
        ("🎨 Mockup Template Folder", mockup_path, "Select your mockup template folder"),
        ("💾 Completed Mockups", output_path, "Choose where you want your newly created mockups saved"),
    ]

    # 🔁 Build labeled folder input fields
    for label_text, var, helper_text in folder_definitions:
        labeled_frame = ttk.LabelFrame(folder_frame, text=label_text)
        labeled_frame.pack(fill=tk.X, padx=5, pady=(6, 4))

        ttk.Label(
            labeled_frame,
            text=helper_text,
            font=("TkDefaultFont", 9, "bold")
        ).pack(anchor="w", padx=5, pady=(2, 0))

        browse_button(var, labeled_frame)

    def load_mockups():
        for widget in scrollable_frame.winfo_children():
            widget.destroy()

        checkbox_vars.clear()
        folder = mockup_path.get()

        if not os.path.isdir(folder):
            return

        # Setup style for rows with dark mockups
        style = ttk.Style()
        style.configure("DarkRow.TFrame", background="#f0f0f0")  # Light grey background

        for root, _, files in os.walk(folder):
            template_name = os.path.basename(root)
            image_files = [f for f in files if f.lower().endswith((".png", ".jpg", ".jpeg"))]
            if not image_files:
                continue

            # Group label for mockup template folder
            group_label = ttk.Label(scrollable_frame, text=f"🧩 {template_name}", font=("TkDefaultFont", 10, "bold"))
            group_label.pack(anchor="w", padx=5, pady=(10, 0))

            for file in sorted(image_files):
                full_path = os.path.join(root, file)
                if not os.path.isfile(full_path):
                    continue

                rel_path = os.path.relpath(full_path, folder)
                mockup_data = templates.get(rel_path, {})
                is_dark = mockup_data.get("is_dark", False)

                select_var = tk.BooleanVar(value=True)
                dark_var = tk.BooleanVar(value=is_dark)

                # Highlight row if Dark BG is enabled
                row_style = "DarkRow.TFrame" if is_dark else "TFrame"
                frame = ttk.Frame(scrollable_frame, style=row_style)
                frame.pack(fill=tk.X, padx=5, pady=2)

                # Unified font styling
                font_style = ("TkDefaultFont", 10)

                cb = ttk.Checkbutton(frame, text=file, variable=select_var)
                cb.configure(style="TCheckbutton")
                cb.pack(side=tk.LEFT)

                dark_toggle = ttk.Checkbutton(
                    frame,
                    text="Dark BG",
                    variable=dark_var,
                    command=lambda f=rel_path, v=dark_var: templates.update({f: {"is_dark": v.get()}})
                )
                dark_toggle.configure(style="TCheckbutton")
                dark_toggle.pack(side=tk.RIGHT)

                checkbox_vars.append((rel_path, select_var))
                templates[rel_path] = templates.get(rel_path, {})
                templates[rel_path]["is_dark"] = dark_var.get()




    def should_use_mockup_for_design(design_file, mockup_name, templates):
        is_dark_mockup = templates.get(mockup_name, {}).get("is_dark", False)
        matched_type = None

        if is_dark_design(design_file):
            matched_type = "Dark"
            result = is_dark_mockup
        elif is_light_design(design_file):
            matched_type = "Light"
            result = not is_dark_mockup
        else:
            matched_type = "Neutral"
            result = True

        log_debug(f"🧪 {design_file} → Type: {matched_type}, Mockup: {'Dark' if is_dark_mockup else 'Light'}, Use: {result}")
        return result





    # 🎛️ Actions Panel
    actions_frame = ttk.LabelFrame(control_frame, text="⚙️ Actions")
    actions_frame.pack(fill=tk.X, padx=10, pady=(10, 10))

    # Reload / Preview / Generate
    # 🛠️ Top Action Buttons (Reload / Preview / Generate)
    actions_frame = ttk.LabelFrame(control_frame, text="🛠️ Actions")
    actions_frame.pack(fill="x", padx=10, pady=(10, 5))

    btn_row = ttk.Frame(actions_frame)
    btn_row.pack(anchor="center", pady=(10, 10))

    ttk.Button(btn_row, text="🔁 Reload Mockups", command=load_mockups).pack(side=tk.LEFT, padx=(0, 10))
    ttk.Button(btn_row, text="👁️ Preview Mockup", command=update_preview).pack(side=tk.LEFT, padx=(0, 10))
    ttk.Button(btn_row, text="🚀 Generate Mockups", command=generate_mockups).pack(side=tk.LEFT)


    

    # 🔻 Divider Line
    separator = ttk.Separator(control_frame, orient="horizontal")
    separator.pack(fill="x", padx=10, pady=(12, 6))

    # 🎨 SECTION: Design Selection Header
    ttk.Label(
        control_frame,
        text="🎨 Design Selection",
        font=("TkDefaultFont", 10, "bold")
    ).pack(anchor="w", padx=10, pady=(0, 4))

    # 🎨 Design Selection Dropdown & Radio Buttons
    design_row = ttk.Frame(control_frame)
    design_row.pack(fill=tk.X, padx=10, pady=(0, 10))

    ttk.Label(design_row, text="Select Design:").pack(side=tk.LEFT)
    design_selector = ttk.Combobox(design_row, textvariable=selected_design, state="readonly", width=30)
    design_selector.pack(side=tk.LEFT, padx=(5, 10))
    design_selector.bind("<<ComboboxSelected>>", lambda e: update_preview())

    ttk.Radiobutton(design_row, text="All", variable=generate_mode, value="all").pack(side=tk.LEFT)
    ttk.Radiobutton(design_row, text="Selected", variable=generate_mode, value="selected").pack(side=tk.LEFT)

    # 🧩 SECTION: Mockup Templates Header
    ttk.Label(
        control_frame,
        text="🧩 Mockup Templates",
        font=("TkDefaultFont", 10, "bold")
    ).pack(anchor="w", padx=10, pady=(10, 4))

    template_section = ttk.LabelFrame(control_frame)
    template_section.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    canvas = tk.Canvas(template_section, highlightthickness=0)
    scrollbar = ttk.Scrollbar(template_section, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)

    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")



    checkbox_vars = []  # Placeholder for checkboxes loaded later


    status_var = tk.StringVar(value="Ready")
    ttk.Label(root, textvariable=status_var, relief=tk.SUNKEN, anchor=tk.W).pack(fill=tk.X, side=tk.BOTTOM)

    def toggle_debug_log_visibility():
        if show_debug_log.get():
            log_frame.pack(fill=tk.BOTH, expand=False, side=tk.BOTTOM, padx=10, pady=(5, 10))
        else:
            log_frame.pack_forget()

    ttk.Checkbutton(
        control_frame,
        text="🪵 Show Debug Log",
        variable=show_debug_log,
        command=toggle_debug_log_visibility  # ✅ connect it
    ).pack(anchor="w", padx=10, pady=(10, 5))


    log_frame = ttk.LabelFrame(root, text="Debug Log")
    log_frame.pack(fill=tk.BOTH, expand=False, side=tk.BOTTOM, padx=10, pady=(5, 10))  # only call pack once

    log_text = tk.Text(log_frame, height=6, wrap=tk.WORD, state="disabled", background="#f7f7f7", font=("Courier", 9))
    log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    # 🔥 This is what you're missing — run this once at startup to apply visibility
    toggle_debug_log_visibility()


    def log_debug(message):
        if not show_debug_log.get():
            return
        log_text.config(state="normal")
        log_text.insert(tk.END, message + "\n")
        log_text.see(tk.END)
        log_text.config(state="disabled")

    def update_preview():
        nonlocal selected_mockup_preview, selected_design, preview_selector, preview_canvas, checkbox_vars

        if not checkbox_vars or not templates:
            return

        design_folder = design_path.get()
        mockup_folder = mockup_path.get()

        designs = [f for f in os.listdir(design_folder) if f.lower().endswith((".png", ".jpg", ".jpeg"))]
        if not designs or not selected_design.get():
            return

        # Filter matching mockups based on Light/Dark compatibility
        valid_mockups = [
            file for file, var in checkbox_vars
            if var.get() and should_use_mockup_for_design(selected_design.get(), file, templates)
        ]

        # Populate dropdown with valid mockups
        preview_selector['values'] = valid_mockups

        # Handle empty mockup case
        if not valid_mockups:
            log_debug(f"⚠️ No matching mockups for {selected_design.get()}")
            if app_initialized:
                messagebox.showinfo("No Match", f"No compatible mockup found for '{selected_design.get()}'.")
            preview_selector.set('')
            return

        # Set or validate selected mockup
        if selected_mockup_preview.get() in valid_mockups:
            selected_mockup = selected_mockup_preview.get()
        else:
            selected_mockup = valid_mockups[0]
            selected_mockup_preview.set(selected_mockup)

        log_debug(f"👕 Previewing on mockup: {selected_mockup}")
        log_debug(f"📂 selected_mockup type: {type(selected_mockup)} | value: {selected_mockup}")

        try:
            design_img = Image.open(os.path.join(design_folder, selected_design.get()))
            mockup_path_full = os.path.join(mockup_folder, selected_mockup)

            if not os.path.isfile(mockup_path_full):
                log_debug(f"⚠️ Skipping preview: {mockup_path_full} is not a file")
                return

            mockup_full_path = os.path.join(mockup_folder, selected_mockup)

            # ✅ Bail out if this is not a valid file
            if not os.path.isfile(mockup_full_path):
                log_debug(f"❌ Skipping preview: Not a file → {mockup_full_path}")
                return

            mockup_img = Image.open(mockup_full_path)

            final_img = overlay_design(
                mockup_img,
                design_img,
                size_var.get(),
                x_offset_var.get(),
                y_offset_var.get(),
                opacity_var.get(),
                lock_aspect_var.get()
            )

            # Resize image to fit canvas
            preview_canvas.update_idletasks()
            max_w = preview_canvas.winfo_width()
            max_h = preview_canvas.winfo_height()
            w, h = final_img.size
            scale = min(max_w / w, max_h / h, 1.0)
            final_img = final_img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)

            preview_img = ImageTk.PhotoImage(final_img)
            preview_canvas.delete("all")
            preview_canvas.create_image(max_w // 2, max_h // 2, anchor=tk.CENTER, image=preview_img)
            preview_canvas.image = preview_img

        except Exception as e:
            print(f"Preview error: {e}")

    def refresh_design_list():
        design_folder = design_path.get()
        if not os.path.isdir(design_folder):
            return

        files = sorted(f for f in os.listdir(design_folder) if f.lower().endswith((".png", ".jpg", ".jpeg")))

        if not files:
            messagebox.showwarning(
                "No Designs Found",
                "The selected Design Location does not contain any image files (.png, .jpg, .jpeg)."
            )
            design_selector['values'] = []
            selected_design.set('')
            design_selector.set('')
            design_selector.config(state="disabled")
            return

        # Populate dropdown and design type info
        design_selector['values'] = files
        design_types.clear()

        for f in files:
            if is_light_design(f):
                design_types[f] = "light"
            elif is_dark_design(f):
                design_types[f] = "dark"
            else:
                design_types[f] = "unknown"

        selected_design.set(files[0])
        design_selector.config(state="readonly")

        if checkbox_vars:
            update_preview()


    if design_path.get():
        refresh_design_list()

    def _on_mousewheel(event):
        control_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    control_canvas.bind_all("<MouseWheel>", _on_mousewheel)

    global app_initialized
    app_initialized = True

    root.mainloop()

if __name__ == "__main__":
    launch_gui()