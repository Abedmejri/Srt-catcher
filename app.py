import whisper
from deep_translator import GoogleTranslator
from gtts import gTTS
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
from moviepy import VideoFileClip, AudioFileClip
import threading

# Function to extract audio from MP4 file
def extract_audio_from_video(video_path, audio_path="extracted_audio.mp3"):
    try:
        with VideoFileClip(video_path) as video:
            video.audio.write_audiofile(audio_path)
        return audio_path
    except Exception as e:
        raise RuntimeError(f"Failed to extract audio: {str(e)}")

# Function to replace audio in the MP4 video with the translated audio
def replace_audio_in_video(video_path, translated_audio_path, output_video_path):
    try:
        with VideoFileClip(video_path) as video, AudioFileClip(translated_audio_path) as translated_audio:
            video_with_new_audio = video.set_audio(translated_audio)
            video_with_new_audio.write_videofile(output_video_path, codec='libx264', audio_codec='aac')
    except Exception as e:
        raise RuntimeError(f"Failed to replace audio: {str(e)}")

# Function to process audio and generate translations and subtitles
def process_audio(video_path, progress_label):
    try:
        progress_label.config(text="Extracting audio...")
        audio_path = extract_audio_from_video(video_path)

        progress_label.config(text="Loading Whisper model...")
        model = whisper.load_model("base")

        progress_label.config(text="Transcribing the audio file...")
        result = model.transcribe(audio_path)
        segments = result["segments"]
        original_text = result['text']

        progress_label.config(text="Translating text to French...")
        translated_texts = [(seg["start"], seg["end"], GoogleTranslator(source='auto', target='fr').translate(seg["text"])) for seg in segments]

        progress_label.config(text="Saving subtitles...")
        srt_file_path = os.path.splitext(video_path)[0] + "_translated.srt"
        with open(srt_file_path, 'w', encoding='utf-8') as srt_file:
            for idx, (start, end, text) in enumerate(translated_texts):
                srt_file.write(f"{idx + 1}\n{format_time(start)} --> {format_time(end)}\n{text}\n\n")

        progress_label.config(text="Generating translated audio...")
        translated_audio_path = os.path.splitext(video_path)[0] + "_translated.mp3"
        tts = gTTS(" ".join([t[2] for t in translated_texts]), lang='fr')
        tts.save(translated_audio_path)

        progress_label.config(text="Replacing audio in video...")
        output_video_path = os.path.splitext(video_path)[0] + "_translated.mp4"
        replace_audio_in_video(video_path, translated_audio_path, output_video_path)

        messagebox.showinfo("Success", f"Process completed! Translated video saved as:\n{output_video_path}")
        progress_label.config(text="Done.")
    except Exception as e:
        messagebox.showerror("Error", str(e))
        progress_label.config(text="Error occurred.")

# Helper function to format time in SRT format (HH:MM:SS,MMM)
def format_time(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    ms = int((s - int(s)) * 1000)
    return f"{int(h):02}:{int(m):02}:{int(s):02},{ms:03}"

# Thread-safe function to handle video processing
def process_video_thread(video_path, progress_label):
    threading.Thread(target=process_audio, args=(video_path, progress_label)).start()

# Setting up the GUI
def create_gui():
    root = tk.Tk()
    root.title("Video Translator and Subtitle Generator")
    root.geometry("450x250")
    root.resizable(False, False)

    label = tk.Label(root, text="Select an MP4 video file to extract audio, transcribe, and translate.", wraplength=400)
    label.pack(pady=10)

    progress_label = tk.Label(root, text="Idle", fg="blue")
    progress_label.pack(pady=5)

    def browse_file():
        file_path = filedialog.askopenfilename(title="Select MP4 Video", filetypes=[("MP4 files", "*.mp4")])
        if file_path:
            progress_label.config(text="Processing...")
            process_video_thread(file_path, progress_label)

    process_button = ttk.Button(root, text="Select Video and Process", command=browse_file)
    process_button.pack(pady=20)

    exit_button = ttk.Button(root, text="Exit", command=root.quit)
    exit_button.pack(pady=5)

    root.mainloop()

# Run the application
if __name__ == "__main__":
    create_gui()
