from flask import Flask, request, render_template, send_file, jsonify
from werkzeug.utils import secure_filename
import os
from deep_translator import GoogleTranslator
from gtts import gTTS
from moviepy import VideoFileClip, AudioFileClip
import whisper
import threading

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['PROCESSED_FOLDER'] = 'processed'

# Ensure folders exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['PROCESSED_FOLDER'], exist_ok=True)

# Function to extract audio from MP4 file
def extract_audio_from_video(video_path, audio_path="extracted_audio.mp3"):
    with VideoFileClip(video_path) as video:
        video.audio.write_audiofile(audio_path)
    return audio_path

# Function to replace audio in the MP4 video with the translated audio
def replace_audio_in_video(video_path, translated_audio_path, output_video_path):
    with VideoFileClip(video_path) as video, AudioFileClip(translated_audio_path) as translated_audio:
        video_with_new_audio = video.set_audio(translated_audio)
        video_with_new_audio.write_videofile(output_video_path, codec='libx264', audio_codec='aac')

# Helper function to format time in SRT format (HH:MM:SS,MMM)
def format_time(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    ms = int((s - int(s)) * 1000)
    return f"{int(h):02}:{int(m):02}:{int(s):02},{ms:03}"

# Video processing function
def process_video(video_path):
    try:
        # Extract audio
        audio_path = os.path.join(app.config['PROCESSED_FOLDER'], "extracted_audio.mp3")
        extract_audio_from_video(video_path, audio_path)

        # Load Whisper model
        model = whisper.load_model("base")

        # Transcribe audio
        result = model.transcribe(audio_path)
        segments = result["segments"]
        original_text = result['text']

        # Translate text
        translated_texts = [(seg["start"], seg["end"], GoogleTranslator(source='auto', target='fr').translate(seg["text"])) for seg in segments]

        # Save subtitles
        srt_file_path = os.path.splitext(video_path)[0] + "_translated.srt"
        with open(srt_file_path, 'w', encoding='utf-8') as srt_file:
            for idx, (start, end, text) in enumerate(translated_texts):
                srt_file.write(f"{idx + 1}\n{format_time(start)} --> {format_time(end)}\n{text}\n\n")

        # Generate translated audio
        translated_audio_path = os.path.splitext(video_path)[0] + "_translated.mp3"
        tts = gTTS(" ".join([t[2] for t in translated_texts]), lang='fr')
        tts.save(translated_audio_path)

        # Replace audio in video
        output_video_path = os.path.splitext(video_path)[0] + "_translated.mp4"
        replace_audio_in_video(video_path, translated_audio_path, output_video_path)

        return {
            "srt_file": srt_file_path,
            "translated_audio": translated_audio_path,
            "output_video": output_video_path
        }
    except Exception as e:
        raise RuntimeError(f"Error processing video: {str(e)}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        def process_and_respond():
            try:
                results = process_video(file_path)
                response = {
                    "message": "Processing completed successfully!",
                    "srt_file": results["srt_file"],
                    "translated_audio": results["translated_audio"],
                    "output_video": results["output_video"]
                }
                with open(os.path.join(app.config['PROCESSED_FOLDER'], f"{filename}_response.json"), "w") as f:
                    f.write(jsonify(response).get_data(as_text=True))
            except Exception as e:
                with open(os.path.join(app.config['PROCESSED_FOLDER'], f"{filename}_error.txt"), "w") as f:
                    f.write(str(e))

        threading.Thread(target=process_and_respond).start()
        return jsonify({"message": "Processing started. Please wait..."})

@app.route('/download/<path:filename>')
def download_file(filename):
    return send_file(filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
