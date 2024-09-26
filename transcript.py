import os
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import assemblyai as aai
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

UPLOAD_FOLDER = 'temp_file'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ASSEMBLY_API_KEY = os.getenv("ASSEMBLY_API_KEY")

# Configuring AssemblyAI
aai.settings.api_key = ASSEMBLY_API_KEY

@app.route('/transcribe', methods=['POST'])
def transcribe():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    
    try:
        transcript = transcribe_audio(file_path)
        os.remove(file_path)
        return jsonify({"transcript": transcript})
    except Exception as e:
        os.remove(file_path)
        return jsonify({"error": str(e)}), 500

def transcribe_audio(file_path):
    '''Passing the recorded audio or uploaded audio file to the 
    assembly ai for getting transcript from the audio.'''
    try:
        transcriber = aai.Transcriber()
        transcript = transcriber.transcribe(file_path)
        return transcript.text
    except Exception as e:
        print(f"Error during transcription: {str(e)}")
        raise Exception("Transcription failed")

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True, port=5001)
