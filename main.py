from tkinter import *
from tkinter import filedialog, messagebox
from tkinter.ttk import Progressbar
import threading
import cv2
from ImageAnalysis import analyze_image
from LiveFeed import analyze_live_feed, stop_live_feed
from database import connect_to_db
from logging_config import logger

class MilitaryImageAnalysisApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Military Image Analysis System")
        self.image_path = None
        self.live_feed_active = False

        self.create_widgets()

    def create_widgets(self):
        self.entry = Entry(self.root, width=50)
        self.entry.pack(pady=10)

        self.button_upload = Button(self.root, text="Upload Image", command=self.upload_image)
        self.button_upload.pack(pady=10)

        self.button_analyze = Button(self.root, text="Analyze Image", command=self.analyze)
        self.button_analyze.pack(pady=10)

        self.button_live_feed = Button(self.root, text="Start Live Feed", command=self.toggle_live_feed)
        self.button_live_feed.pack(pady=10)

        self.progress_bar = Progressbar(self.root, orient=HORIZONTAL, length=300, mode='determinate')
        self.progress_bar.pack(pady=10)

        self.label = Label(self.root, text="", font=("Arial", 12))
        self.label.pack(pady=10)

        self.root.protocol("WM_DELETE_WINDOW", self.close_window)

    def upload_image(self):
        self.image_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.jpeg;*.png")])
        if self.image_path:
            self.entry.delete(0, END)
            self.entry.insert(0, self.image_path)
            self.label.config(text="Image uploaded successfully.")

    def analyze(self):
        if not self.image_path:
            messagebox.showwarning("Warning", "Please upload an image first.")
            return

        self.progress_bar['value'] = 0
        self.label.config(text="Analyzing...")

        def analyze_thread():
            try:
                image = cv2.imread(self.image_path)
                if image is None:
                    messagebox.showerror("Error", "Invalid image!")
                    return

                result = analyze_image(image, progress_callback=self.update_progress)
                if result:
                    name, age, nationality, crime, danger_level, ip = result
                    self.label.config(
                        text=f"Name: {name}\nAge: {age}\nNationality: {nationality}\nCrime: {crime}\nDanger Level: {danger_level}\nNetwork IP: {ip}"
                    )
                else:
                    self.label.config(text="No information found.")
            except Exception as e:
                logger.error(f"Error during analysis: {e}")
                messagebox.showerror("Error", "An error occurred during analysis.")

        threading.Thread(target=analyze_thread, daemon=True).start()

    def toggle_live_feed(self):
        if not self.live_feed_active:
            self.live_feed_active = True
            self.button_live_feed.config(text="Stop Live Feed")
            threading.Thread(target=analyze_live_feed, daemon=True).start()
        else:
            self.live_feed_active = False
            self.button_live_feed.config(text="Start Live Feed")
            stop_live_feed()

    def update_progress(self, value):
        self.progress_bar['value'] = value
        self.root.update_idletasks()

    def close_window(self):
        try:
            if db:
                db.close()
                logger.info("Database connection closed.")
        except Exception as e:
            logger.error(f"Error closing database connection: {e}")
        self.root.quit()

if __name__ == "__main__":
    db = connect_to_db()
    if db:
        root = Tk()
        app = MilitaryImageAnalysisApp(root)
        root.mainloop()