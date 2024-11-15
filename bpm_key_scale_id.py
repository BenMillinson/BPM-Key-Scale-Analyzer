import os
import tkinter as tk
from tkinter import filedialog, messagebox
import librosa
import numpy as np
from essentia.standard import KeyExtractor
import threading

class MusicAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("BPM, Key, and Scale Analyzer")
        self.root.geometry("475x525")
        self.loading_label = None

        # Set a consistent background color for the GUI
        self.bg_color = "#f0f0f0"
        self.root.config(bg=self.bg_color)

        # GUI Elements
        self.upload_button = tk.Button(self.root, text="Upload Audio File", command=self.open_file, bg="#4CAF50", fg="black", font=("Arial", 12))
        self.upload_button.pack(pady=20)

        # Label to display the selected file name
        self.file_name_label = tk.Label(self.root, text="No file selected", fg="blue", bg=self.bg_color)
        self.file_name_label.pack(pady=5)

        # Text box to show results
        self.result_text = tk.Text(self.root, height=10, width=60, wrap=tk.WORD, state=tk.DISABLED, bg="white")
        self.result_text.pack(pady=10)

        # Canvas for loading animation (this could be a simple circle or spinner)
        self.canvas = tk.Canvas(self.root, width=200, height=200, bg=self.bg_color, highlightthickness=0)
        self.canvas.pack(pady=10)

    def open_file(self):
        """Open file dialog to select an audio file."""
        file_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.mp3 *.wav *.flac")])
        if file_path:
            self.display_selected_file(file_path)
            self.analyze_music_in_thread(file_path)

    def display_selected_file(self, file_path):
        """Display the name of the selected file in the GUI."""
        file_name = os.path.basename(file_path)
        self.file_name_label.config(text=f"Selected File: {file_name}")

    def analyze_music_in_thread(self, file_path):
        """Start analyzing the music in a separate thread."""
        self.display_loading()
        threading.Thread(target=self.process_audio, args=(file_path,)).start()

    def process_audio(self, file_path):
        """Handles the audio processing in a separate thread."""
        bpm, key, scale = self.analyze_music(file_path)

        
        self.root.after(0, lambda: self.display_results(bpm, key, scale))

    def analyze_music(self, file_path):
        """Analyze the audio file and extract BPM and key."""
        # Load audio file with librosa
        y, sr = librosa.load(file_path)

        # Estimate BPM
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)

        # Check if tempo is an ndarray, and if so, get the first element
        if isinstance(tempo, np.ndarray):
            tempo = tempo[0]

        # Estimate Key using Essentia KeyExtractor
        key_extractor = KeyExtractor()
        result = key_extractor(y)
        
        # Extract the key and scale from the result
        key, scale = result[0], result[1]

        return tempo, key, scale

    def display_loading(self):
        """Displays the loading spinner while processing."""
        self.loading_label = tk.Label(self.root, text="Analyzing...", fg="black", bg=self.bg_color, font=("Arial", 12))  # Black text
        self.loading_label.pack(pady=5)

        # Create a loading spinner
        self.loading_circle(self.canvas, 100, 100, 40)  

    def loading_circle(self, canvas, x, y, radius):
        """Draw a spinning circle for the loading indicator."""
        self.angle = 0
        self.spinner = canvas.create_arc(
            x - radius, y - radius, x + radius, y + radius,
            start=self.angle, extent=90, outline="black", width=5, style="arc"
        )
        self.spin_circle()

    def spin_circle(self):
        """Spins the circle."""
        self.angle += 10
        if self.angle >= 360:
            self.angle = 0
        self.canvas.itemconfig(self.spinner, start=self.angle)
        self.root.after(50, self.spin_circle)

    def display_results(self, bpm, key, scale):
        """Updates the result display after processing is finished."""
        # Hide loading elements
        self.loading_label.pack_forget()
        self.canvas.pack_forget()

        # Display results in the text box
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)  # Clear previous results
        self.result_text.insert(tk.END, f"BPM (Tempo): {bpm:.2f} BPM\n")
        self.result_text.insert(tk.END, f"Key: {key}\n")
        self.result_text.insert(tk.END, f"Scale: {scale}\n")
        self.result_text.config(state=tk.DISABLED)

# Main Application Execution
if __name__ == "__main__":
    root = tk.Tk()  # Use standard Tkinter for GUI
    app = MusicAnalyzerApp(root)
    root.mainloop()
