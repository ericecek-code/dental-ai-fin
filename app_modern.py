from flask import Flask, request, jsonify, send_from_directory, abort
import uuid
from pathlib import Path
import os

# Dentscope-modernized baseline: keep upload + enhancement + detection
# working but move core behavior behind safer defaults and expose
color-coded feedback in responses.

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = Path('uploads')
app.config['ENHANCED_FOLDER'] = Path('enhanced')
app.config['DETECTED_FOLDER'] = Path('detected')

for folder in (app.config['UPLOAD_FOLDER'], app.config['ENHANCED_FOLDER'], app.config['DETECTED_FOLDER']):
    folder.mkdir(parents=True, exist_ok=True)

# Allowed file extensions for dental radiographs/dicom-derived images
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'dcm', 'tif', 'tiff'}


def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'}), 200


@app.route('/api', methods=['GET'])
def api_root():
    return jsonify({
        'name': 'Dental-Disease-Detection Modernized',
        'status': 'running',
        'endpoints': [
            '/health',
            '/api/upload',
            '/api/detect',
            '/uploads/<filename>',
            '/enhanced/<filename>',
            '/detected/<filename>'
        ]
    })


@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Empty filename'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Unsupported file type'}), 400

    base, ext = os.path.splitext(file.filename)
    filename = f"{base}_{uuid.uuid4().hex[:8]}{ext}"
    input_path = app.config['UPLOAD_FOLDER'] / filename

    file.save(str(input_path))
    return jsonify({'uploaded': True, 'filename': filename}), 201


@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(str(app.config['UPLOAD_FOLDER']), filename)


@app.route('/enhanced/<path:filename>')
def enhanced_file(filename):
    return send_from_directory(str(app.config['ENHANCED_FOLDER']), filename)


@app.route('/detected/<path:filename>')
def detected_file(filename):
    return send_from_directory(str(app.config['DETECTED_FOLDER']), filename)


