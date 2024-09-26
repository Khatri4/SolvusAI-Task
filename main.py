import os
import requests
from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'wav', 'mp3'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

TRANSCRIPTION_SERVICE_URL = 'http://localhost:5001/transcribe'
REPORT_SERVICE_URL = 'http://localhost:5002/generate-report'

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process-audio', methods=['POST'])
def process_audio():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file and (allowed_file(file.filename) or file.filename == 'recorded_audio.wav'):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Send file to transcription service
        with open(file_path, 'rb') as audio_file:
            files = {'file': (filename, audio_file)}
            transcription_response = requests.post(TRANSCRIPTION_SERVICE_URL, files=files)
        
        if transcription_response.status_code != 200:
            return jsonify({"error": "Transcription failed"}), 500
        
        transcript = transcription_response.json()['transcript']
        
        # Send transcript to report generation service
        report_response = requests.post(REPORT_SERVICE_URL, json={'transcript': transcript})
        
        if report_response.status_code != 200:
            return jsonify({"error": "Report generation failed"}), 500
        
        medical_report = report_response.json()['medical_report']
        
        # Clean up the temporary file
        os.remove(file_path)
        
        return jsonify({"transcript": transcript, "medical_report": medical_report})
    return jsonify({"error": "File type not allowed"}), 400

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True, port=5000)

