# Video Translation Web Application

This project is a Flask-based web application that processes videos to extract audio, transcribe it using the Whisper model, translate it into French, and replace the original audio with the translated version. The app also generates subtitles in `.srt` format.

## Features
- Extract audio from uploaded MP4 videos.
- Transcribe audio using OpenAI's Whisper model.
- Translate the transcription into French using the Google Translator API.
- Generate translated audio using Google Text-to-Speech (gTTS).
- Replace the original video audio with the translated audio.
- Provide `.srt` subtitles for the translated video.

## Prerequisites
- Python 3.7+
- Required libraries (install via `pip`):
  - Flask
  - moviepy
  - whisper
  - deep-translator
  - gTTS

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/video-translation-web.git
   cd video-translation-web
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

   Example `requirements.txt` file:
   ```
   Flask
   moviepy
   whisper
   deep-translator
   gTTS
   ```

3. Ensure the following folders exist (they will be created if not):
   - `uploads`: For storing uploaded videos.
   - `processed`: For storing processed files.

## Usage

1. Start the Flask application:
   ```bash
   python app.py
   ```

2. Open your browser and navigate to:
   ```
   http://127.0.0.1:5000
   ```

3. Upload an MP4 video to start the processing. A loading screen will indicate progress.

4. After processing, download the translated video, subtitles, or audio from the links provided.

## File Structure
- `app.py`: Main Flask application.
- `templates/index.html`: Frontend interface for the web application.
- `uploads/`: Directory for uploaded videos.
- `processed/`: Directory for processed files (e.g., subtitles, translated videos).

## How It Works

1. **Upload Video**: The user uploads an MP4 file through the web interface.
2. **Processing**:
   - Extracts audio from the video.
   - Transcribes audio using Whisper.
   - Translates transcription into French.
   - Generates translated audio using gTTS.
   - Replaces original audio in the video with the translated version.
3. **Output**:
   - A new video with translated audio.
   - An `.srt` file with subtitles.

## Notes
- Processing time depends on the video length and server performance.
- The Whisper model requires significant computational resources; consider running on a machine with a GPU for faster processing.

## Contributing
Feel free to submit issues or pull requests for improvements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for details.

