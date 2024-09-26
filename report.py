import os
from flask import Flask, request, jsonify
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Configuring Google Generative AI
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro')

@app.route('/generate-report', methods=['POST'])
def generate_report():
    data = request.json
    if 'transcript' not in data:
        return jsonify({"error": "No transcript provided"}), 400
    
    try:
        medical_report = generate_medical_report(data['transcript'])
        return jsonify({"medical_report": medical_report})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def generate_medical_report(transcript):
    '''Passing the transcript that we got from the assembly ai 
    to the gemini model and giving the prompt to gemini model to 
    perform the summarization task and give me summary as the medical report.'''

    prompt = f"""
    You are doctor. Based on the following conversation with patient, generate a structured medical report. Include the following sections:

    1. Patient Information
    2. Chief Complaint
    3. History of Present Illness
    4. Past Medical History
    5. Medications
    6. Allergies
    7. Physical Examination
    8. Assessment
    9. Plan

    If any section cannot be filled due to lack of information, state "Information not provided".

    Conversation transcript:
    {transcript}

    Please format the report in Markdown.
    """

    response = model.generate_content(prompt)
    return response.text

if __name__ == '__main__':
    app.run(debug=True, port=5002)
