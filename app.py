from flask import Flask, request, jsonify
from aadhar_ocr import process_aadhar
import os

app = Flask(__name__)

@app.route('/extract-aadhar', methods=['POST'])
def extract_aadhar():
    front_file = request.files.get('front_image')
    back_file = request.files.get('back_image')

    if not front_file or not back_file:
        return jsonify({"error": "Missing front or back image"}), 400

    # Define temp file paths
    front_path = 'temp_front.jpg'
    back_path = 'temp_back.jpg'

    # Save uploaded files to disk
    front_file.save(front_path)
    back_file.save(back_path)

    # Now the paths exist, so you're safe to proceed
    extracted_data = process_aadhar(front_path, back_path)

    # Optionally clean up the files after processing
    os.remove(front_path)
    os.remove(back_path)

    return jsonify(extracted_data)

if __name__ == "__main__":
    app.run(debug=True)
