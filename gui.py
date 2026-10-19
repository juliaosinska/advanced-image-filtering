
#GenAI: Gemini for GUI implementation

import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageTk
from convolution import apply_filter

class ImageFilterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Custom Image Filter App")
        self.root.geometry("900x600")

        self.image_path = None
        self.original_image = None
        self.filtered_image = None

        # --- Control Panel Frame ---
        control_frame_top = tk.Frame(root, pady=10)
        control_frame_top.pack(side=tk.TOP, fill=tk.X)

        self.upload_btn = tk.Button(control_frame_top, text="Upload Image", command=self.upload_image)
        self.upload_btn.pack(side=tk.LEFT, padx=10)

        self.filter_var = tk.StringVar(value="Averaging")
        self.filter_dropdown = ttk.Combobox(control_frame_top, textvariable=self.filter_var, 
                                            values=["Averaging", "Sharpening", "Gaussian", "Laplacian"], state="readonly")
        self.filter_dropdown.pack(side=tk.LEFT, padx=10)

        # Combined event handler for dropdown changes
        self.filter_dropdown.bind("<<ComboboxSelected>>", self.on_filter_changed)

        # Optimization Checkbox Switch
        self.optimized_var = tk.BooleanVar(value=True)
        self.optimized_checkbox = tk.Checkbutton(control_frame_top, text="Use Vectorized Optimization", variable=self.optimized_var, command=self.reset_filter_output)
        self.optimized_checkbox.pack(side=tk.LEFT, padx=10)

        self.filter_btn = tk.Button(control_frame_top, text="Filter", command=self.process_image)
        self.filter_btn.pack(side=tk.LEFT, padx=10)

        self.save_btn = tk.Button(control_frame_top, text="Save Filtered Image", command=self.save_image)
        self.save_btn.pack(side=tk.LEFT, padx=10)

        # --- Control Panel Frame (Row 2: Sliders for Parameters) ---
        self.control_frame_bottom = tk.Frame(root, pady=5)
        self.control_frame_bottom.pack(side=tk.TOP, fill=tk.X)

        # 1. Kernel Size Frame (used by Averaging and Gaussian)
        self.size_frame = tk.Frame(self.control_frame_bottom)
        tk.Label(self.size_frame, text="Kernel Size:").pack(side=tk.LEFT, padx=(10, 2))
        self.size_var = tk.StringVar(value="3")
        self.size_dropdown = ttk.Combobox(self.size_frame, textvariable=self.size_var, values=["3", "5", "7", "9"], width=5, state="readonly")
        self.size_dropdown.pack(side=tk.LEFT, padx=5)
        self.size_dropdown.bind("<<ComboboxSelected>>", self.reset_filter_output)

        # 2. Sigma Frame (Only for Gaussian)
        self.sigma_frame = tk.Frame(self.control_frame_bottom)
        tk.Label(self.sigma_frame, text="Sigma:").pack(side=tk.LEFT, padx=(10, 2))
        self.sigma_slider = tk.Scale(self.sigma_frame, from_=0.1, to=5.0, resolution=0.1, orient=tk.HORIZONTAL, command=self.reset_filter_output)
        self.sigma_slider.set(1.0)
        self.sigma_slider.pack(side=tk.LEFT, padx=5)

        # 3. Strength Frame (Only for Sharpening)
        self.strength_frame = tk.Frame(self.control_frame_bottom)
        tk.Label(self.strength_frame, text="Strength:").pack(side=tk.LEFT, padx=(10, 2))
        self.strength_slider = tk.Scale(self.strength_frame, from_=0.1, to=5.0, resolution=0.1, orient=tk.HORIZONTAL, command=self.reset_filter_output)
        self.strength_slider.set(1.0)
        self.strength_slider.pack(side=tk.LEFT, padx=5)

        # Trigger visibility check on startup based on default dropdown value
        self.update_controls_visibility()

        # --- Display Panel Frame ---
        display_frame = tk.Frame(root)
        display_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Original Image Window
        self.orig_label_frame = tk.LabelFrame(display_frame, text="Original Image")
        self.orig_label_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        self.orig_canvas = tk.Label(self.orig_label_frame)
        self.orig_canvas.pack(fill=tk.BOTH, expand=True)

        # Filtered Image Window
        self.filt_label_frame = tk.LabelFrame(display_frame, text="Filtered Image")
        self.filt_label_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
        self.filt_canvas = tk.Label(self.filt_label_frame)
        self.filt_canvas.pack(fill=tk.BOTH, expand=True)

    def on_filter_changed(self, event=None):
        self.update_controls_visibility()
        self.reset_filter_output()

    def update_controls_visibility(self):
        selected = self.filter_var.get()
        
        self.size_frame.pack_forget()
        self.sigma_frame.pack_forget()
        self.strength_frame.pack_forget()

        if selected not in ("Laplacian", "Sharpening"):
            self.size_frame.pack(side=tk.LEFT, padx=10)
        
        if selected == "Gaussian":
            self.sigma_frame.pack(side=tk.LEFT, padx=10)
        elif selected == "Sharpening":
            self.strength_frame.pack(side=tk.LEFT, padx=10)

    def reset_filter_output(self, *args):
        self.filtered_image = None
        # Clear the filtered canvas display so the user knows changes were made
        self.filt_canvas.config(image="")
        self.filt_canvas.image = None

    def upload_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.jpeg *.png *.bmp")])
        if file_path:
            self.image_path = file_path
            # Load image using Pillow and ensure it's in RGB mode
            self.original_image = Image.open(file_path).convert("RGB")
            self.display_image(self.original_image, self.orig_canvas)

    def process_image(self):
        if self.original_image is None:
            return
        
        selected_filter = self.filter_var.get()
        sigma_val = self.sigma_slider.get()
        strength_val = self.strength_slider.get()

        size_val = int(self.size_var.get())
        optimized_val = self.optimized_var.get()
        
        self.filtered_image = apply_filter(
            self.original_image, 
            selected_filter, 
            sigma=sigma_val, 
            strength=strength_val,
            kernel_size=size_val,
            optimized=optimized_val
        )
        
        self.display_image(self.filtered_image, self.filt_canvas)

    def save_image(self):
        if self.filtered_image is None:
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")]
        )
        if file_path:
            self.filtered_image.save(file_path)

    def display_image(self, img, canvas):
        # Resize for display fit while maintaining aspect ratio
        img_copy = img.copy()
        img_copy.thumbnail((400, 400))
        img_tk = ImageTk.PhotoImage(img_copy)
        
        canvas.config(image=img_tk)
        canvas.image = img_tk  # Prevent garbage collection

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageFilterApp(root)
    root.mainloop()