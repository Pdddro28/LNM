# ====================================================
# LIBRARIES
# ====================================================
import cv2 as cv
import numpy as np
import json
import datetime
import customtkinter as ctk
from tkinter import filedialog
from PIL import Image
from picamera2 import Picamera2

# ====================================================
# COMPUTER VISION SUBSYSTEM DATA STRUCTURES
# ====================================================
class ROI:
    def __init__(self, x1, y1, x2, y2):
        self.x1, self.y1 = x1, y1
        self.x2, self.y2 = x2, y2

class VisionController():
    def __init__(self):
        self.image_width  = 640
        self.image_height = 370
        self.image_lab = None
        self.frame = None
        
        self.picam2 = Picamera2()
        config = self.picam2.create_video_configuration(
            main={"size": (self.image_width, self.image_height), "format": "RGB888"}
        )
        self.picam2.configure(config)
        self.picam2.start()

    def receive_image(self):
        self.frame = self.picam2.capture_array('main')
        self.frame = cv.flip(self.frame, 0)
        self.frame = cv.flip(self.frame, 1)

        if self.frame is None:
            print("No se pudo obtener imagen de la PiCamera.")
            return

        self.image_lab = cv.cvtColor(self.frame, cv.COLOR_BGR2LAB)
       
        l_channel, a_channel, b_channel = cv.split(self.image_lab)
       
        clahe = cv.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        cl_channel = clahe.apply(l_channel)
       
        self.image_lab = cv.merge((cl_channel, a_channel, b_channel))
       
        self.image_lab = cv.GaussianBlur(self.image_lab, (7, 7), 0)
        return True

    def find_mask(self, color_range, roi):
        img_segmented = self.image_lab[roi.y1:roi.y2, roi.x1:roi.x2]
        lower = np.array(color_range[0])
        upper = np.array(color_range[1])
        
        mask = cv.inRange(img_segmented, lower, upper)
        kernel = np.ones((5, 5), np.uint8)
        mask = cv.erode(mask, kernel, iterations=1)
        mask = cv.dilate(mask, kernel, iterations=1)
        return mask

# ====================================================
# COLOR CALIBRATION PRESETS
# ====================================================
COLOR_PRESETS = {
    0: {"name": "RED",      "lower": [ 30, 170, 120], "upper": [255, 255, 170]},
    1: {"name": "GREEN",    "lower": [ 30,    0, 100], "upper": [255, 100, 160]},
    2: {"name": "BLUE",     "lower": [ 30, 110,    0], "upper": [255, 150, 110]},
    3: {"name": "PURPLE",   "lower": [ 30, 160,    0], "upper": [255, 255, 110]},
    4: {"name": "ORANGE",   "lower": [ 50, 140, 150], "upper": [255, 255, 255]},
    5: {"name": "BLACK",    "lower": [  0,    0,    0], "upper": [ 60, 255, 255]}
}
COLOR_NAMES_LIST = [COLOR_PRESETS[i]["name"] for i in range(len(COLOR_PRESETS))]

# ====================================================
# GRAPHICAL USER INTERFACE APPLICATION
# ====================================================
class VisionApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Vision Calibration System")
        self.geometry("1300x600")
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        self.vision = VisionController()

        self.grid_columnconfigure(0, weight=1) 
        self.grid_columnconfigure(1, weight=0) 
        self.grid_rowconfigure(0, weight=1)

        # --- VIDEO PANEL ---
        self.video_frame = ctk.CTkFrame(self)
        self.video_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.video_label = ctk.CTkLabel(self.video_frame, text="Starting camera...")
        self.video_label.pack(expand=True, fill="both")

        # --- CONTROLS PANEL ---
        self.controls_frame = ctk.CTkFrame(self, width=350)
        self.controls_frame.grid(row=0, column=1, padx=10, pady=10, sticky="ns")

        self.color_var = ctk.StringVar(value="RED")
        self.preset_menu = ctk.CTkOptionMenu(
            self.controls_frame, 
            values=COLOR_NAMES_LIST,
            command=self.load_preset, 
            variable=self.color_var
        )
        self.preset_menu.pack(pady=20, padx=20)

        self.sliders = {}
        self.labels = {}

        def create_slider(name, default_val):
            lbl = ctk.CTkLabel(self.controls_frame, text=f"{name}: {default_val}", font=("Arial", 14, "bold"))
            lbl.pack(padx=20, pady=(5, 0), anchor="w")
            
            sl = ctk.CTkSlider(
                self.controls_frame, from_=0, to=255, 
                command=lambda v: self.update_label_text(name, v)
            )
            sl.set(default_val)
            sl.pack(padx=20, pady=(0, 10))
            
            self.labels[name] = lbl
            self.sliders[name] = sl

        create_slider("L-min", 30)
        create_slider("L-max", 255)
        create_slider("A-min", 170)
        create_slider("A-max", 255)
        create_slider("B-min", 120)
        create_slider("B-max", 170)

        self.save_btn = ctk.CTkButton(self.controls_frame, text="SAVE JSON", command=self.save_json, fg_color="#28a745", hover_color="#218838")
        self.save_btn.pack(pady=20, padx=20)

        self.status_label = ctk.CTkLabel(self.controls_frame, text="Status: READY", text_color="green")
        self.status_label.pack(pady=5)

        self.load_preset("RED")
        self.update_video_stream()

    def update_label_text(self, name, val):
        self.labels[name].configure(text=f"{name}: {int(val)}")

    def load_preset(self, color_name):
        preset = next(item for item in COLOR_PRESETS.values() if item["name"] == color_name)
        
        self.sliders["L-min"].set(preset["lower"][0])
        self.sliders["L-max"].set(preset["upper"][0])
        self.sliders["A-min"].set(preset["lower"][1])
        self.sliders["A-max"].set(preset["upper"][1])
        self.sliders["B-min"].set(preset["lower"][2])
        self.sliders["B-max"].set(preset["upper"][2])

        for name in self.sliders:
            self.update_label_text(name, self.sliders[name].get())

    def save_json(self):
        lower = [int(self.sliders["L-min"].get()), int(self.sliders["A-min"].get()), int(self.sliders["B-min"].get())]
        upper = [int(self.sliders["L-max"].get()), int(self.sliders["A-max"].get()), int(self.sliders["B-max"].get())]
        color_name = self.color_var.get()

        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            initialfile=f"mask_{color_name.lower()}.json",
            title="Save Mask Configuration"
        )

        if file_path:
            config_data = {
                "color": color_name,
                "timestamp": datetime.datetime.now().isoformat(),
                "bounds": {"lower": lower, "upper": upper},
                "space": "LAB"
            }
            try:
                with open(file_path, 'w') as f:
                    json.dump(config_data, f, indent=4)
                self.status_label.configure(text=f"Saved: {file_path.split('/')[-1]}", text_color="#28a745")
            except Exception:
                self.status_label.configure(text="Error saving file", text_color="red")

    def update_video_stream(self):
        if self.vision.receive_image():
            l_min, l_max = int(self.sliders["L-min"].get()), int(self.sliders["L-max"].get())
            a_min, a_max = int(self.sliders["A-min"].get()), int(self.sliders["A-max"].get())
            b_min, b_max = int(self.sliders["B-min"].get()), int(self.sliders["B-max"].get())

            if l_min > l_max: l_max = l_min
            if a_min > a_max: a_max = a_min
            if b_min > b_max: b_max = b_min

            lower = [l_min, a_min, b_min]
            upper = [l_max, a_max, b_max]

            test_roi = ROI(0, 0, self.vision.image_width, self.vision.image_height)
            mask = self.vision.find_mask([lower, upper], test_roi)
            result = cv.bitwise_and(self.vision.frame, self.vision.frame, mask=mask)
            mask_color = cv.cvtColor(mask, cv.COLOR_GRAY2BGR)

            combined_video = np.hstack([self.vision.frame, mask_color, result])
            
            overlay_text1 = f"COLOR: {self.color_var.get()}"
            overlay_text2 = f"MIN: L:{l_min} A:{a_min} B:{b_min}"
            overlay_text3 = f"MAX: L:{l_max} A:{a_max} B:{b_max}"
            
            cv.putText(combined_video, overlay_text1, (20, 40), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)
            cv.putText(combined_video, overlay_text2, (20, 80), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 3)
            cv.putText(combined_video, overlay_text3, (20, 120), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 165, 255), 3)

            combined_video = cv.resize(combined_video, (960, 240))
            
            combined_video_rgb = cv.cvtColor(combined_video, cv.COLOR_BGR2RGB)
            img_pil = Image.fromarray(combined_video_rgb)
            
            ctk_img = ctk.CTkImage(light_image=img_pil, dark_image=img_pil, size=(960, 240))
            self.video_label.configure(image=ctk_img, text="")
            self.video_label.image = ctk_img

        self.after(15, self.update_video_stream)

    def on_closing(self):
        print("Stopping camera...")
        self.vision.picam2.stop()
        self.destroy()

# ====================================================
# ENTRY POINT
# ====================================================
if __name__ == "__main__":
    app = VisionApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
