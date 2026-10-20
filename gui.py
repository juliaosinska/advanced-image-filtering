
#GenAI: Gemini for GUI implementation and updates

import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageTk
from processors import apply_filter
from filters_config import FILTER_CONFIG

class ImageFilterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Custom Image Filter App")
        self.root.geometry("900x600")

        self.image_path = None
        self.original_image = None
        self.filtered_image = None

        # --- 1.Control Panel Frame ---
        control_frame_top = tk.Frame(root, pady=10)
        control_frame_top.pack(side=tk.TOP, fill=tk.X)

        self.upload_btn = tk.Button(control_frame_top, text="Upload Image", command=self.upload_image)
        self.upload_btn.pack(side=tk.LEFT, padx=5)

        # Dynamically populate filter dropdown from FILTER_CONFIG
        self.filter_var = tk.StringVar(value=list(FILTER_CONFIG.keys())[0])
        self.filter_dropdown = ttk.Combobox(
            control_frame_top, 
            textvariable=self.filter_var, 
            values=list(FILTER_CONFIG.keys()), 
            state="readonly",
            width=25
        )
        self.filter_dropdown.pack(side=tk.LEFT, padx=5)
        self.filter_dropdown.bind("<<ComboboxSelected>>", self.on_filter_changed)

        # Optimized checkbox for vectorized optimization
        self.optimized_var = tk.BooleanVar(value=True)
        self.optimized_checkbox = tk.Checkbutton(
            control_frame_top, 
            text="Vectorized Optimization", 
            variable=self.optimized_var, 
            command=self.reset_filter_output
        )
        self.optimized_checkbox.pack(side=tk.LEFT, padx=5)

        self.filter_btn = tk.Button(control_frame_top, text="Apply Filter", command=self.process_image)
        self.filter_btn.pack(side=tk.LEFT, padx=5)

        self.save_btn = tk.Button(control_frame_top, text="Save Filtered Image", command=self.save_image)
        self.save_btn.pack(side=tk.LEFT, padx=5)

        # --- 2. Dynamic Parameters Frame (Row 2) ---
        self.dynamic_params_frame = tk.Frame(root, pady=5)
        self.dynamic_params_frame.pack(side=tk.TOP, fill=tk.X)
        self.param_vars = {}

        # --- 3. Dynamic Preview Container ---
        self.preview_container = tk.Frame(root)
        self.preview_container.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.preview_canvases = {}

        # --- 4. Initialize UI for the current filter ---
        self.rebuild_ui_for_current_filter()

    def on_filter_changed(self, event=None):
        self.rebuild_ui_for_current_filter()
        self.reset_filter_output()

    def rebuild_ui_for_current_filter(self):
        # Clear existing parameter controls
        for widget in self.dynamic_params_frame.winfo_children():
            widget.destroy()
        self.param_vars = {}

        selected_filter = self.filter_var.get()
        filter_config = FILTER_CONFIG.get(selected_filter, {})
        params_def = filter_config.get("params", {})

        # Generate dynamic sliders or controls based on the filter's parameters
        for param_name, meta in params_def.items():
            p_frame = tk.Frame(self.dynamic_params_frame)
            p_frame.pack(side=tk.LEFT, padx=8)

            tk.Label(p_frame, text=meta["label"] + ":").pack(side=tk.LEFT, padx=(0, 2))

            if meta["type"] in ("int", "float"):
                var = tk.DoubleVar(value=meta["default"]) if meta["type"] == "float" else tk.IntVar(value=meta["default"])
                slider = tk.Scale(
                    p_frame,
                    from_=meta["min"],
                    to=meta["max"],
                    resolution=meta["step"],
                    orient=tk.HORIZONTAL,
                    variable=var,
                    command=self.reset_filter_output,
                    length=120
                )
                slider.pack(side=tk.LEFT)
                self.param_vars[param_name] = var

            elif meta["type"] == "select":
                var = tk.StringVar(value=str(meta["default"]))
                combo = ttk.Combobox(p_frame, textvariable=var, values=meta["options"], width=6, state="readonly")
                combo.pack(side=tk.LEFT)
                combo.bind("<<ComboboxSelected>>", self.reset_filter_output)
                self.param_vars[param_name] = var

        # Clear and rebuild the preview grid based on 'previews' from the config
        for widget in self.preview_container.winfo_children():
            widget.destroy()
        self.preview_canvases = {}

        previews_list = filter_config.get("previews", ["Original", "Filtered"])
        for title in previews_list:
            frame = tk.LabelFrame(self.preview_container, text=title)
            frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            canvas = tk.Label(frame)
            canvas.pack(fill=tk.BOTH, expand=True)
            self.preview_canvases[title] = canvas

    def reset_filter_output(self, *args):
        self.results_dict = {}
        for canvas in self.preview_canvases.values():
            canvas.config(image="")
            canvas.image = None

    def upload_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.jpeg *.png *.bmp")])
        if file_path:
            self.image_path = file_path
            # Load image using Pillow and ensure it's in RGB mode
            self.original_image = Image.open(file_path).convert("RGB")
            first_key = list(self.preview_canvases.keys())[0]
            self.display_image(self.original_image, self.preview_canvases[first_key])

    def process_image(self):
        if self.original_image is None:
            return
        
        selected_filter = self.filter_var.get()
        optimized_val = self.optimized_var.get()

        params = {name: var.get() for name, var in self.param_vars.items()}
        
        self.results_dict = apply_filter(
            self.original_image, 
            selected_filter, 
            params=params,
            optimized=optimized_val
        )

        for title, img in self.results_dict.items():
            if title in self.preview_canvases:
                self.display_image(img, self.preview_canvases[title])

    def save_image(self):
        if not hasattr(self, 'results_dict') or not self.results_dict:
            return
        final_img = list(self.results_dict.values())[-1]
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")]
        )
        if file_path:
            final_img.save(file_path)

    def display_image(self, img, canvas):
        # Resize for display fit while maintaining aspect ratio
        img_copy = img.copy()
        img_copy.thumbnail((300, 300))
        img_tk = ImageTk.PhotoImage(img_copy)
        
        canvas.config(image=img_tk)
        canvas.image = img_tk  # Prevent garbage collection

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageFilterApp(root)
    root.mainloop()