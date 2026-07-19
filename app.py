from flask import Flask, render_template, request, send_file, url_for, jsonify, redirect
import os
import subprocess
import threading
import time
import uuid
from werkzeug.utils import secure_filename
from PIL import Image

# Import YOLOv8 if installed, otherwise provide instructions
try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ENHANCED_FOLDER'] = 'enhanced'
app.config['DETECTED_FOLDER'] = 'detected'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create necessary directories if they don't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['ENHANCED_FOLDER'], exist_ok=True)
os.makedirs(app.config['DETECTED_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# YOLOv8 model path
MODEL_PATH = os.path.join('YOLOv8 model', 'best (1).pt')

# Store ongoing processes for cancellation
ongoing_processes = {}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def enhance_image(input_path, output_path, process_id):
    try:
        # Run Real-ESRGAN command
        cmd = f'realesrgan-ncnn-vulkan.exe -i "{input_path}" -o "{output_path}"'
        
        # Start subprocess and store the process
        process = subprocess.Popen(cmd, shell=True)
        ongoing_processes[process_id] = process
        
        # Wait for process to complete
        return_code = process.wait()
        
        # Clean up process from dictionary
        if process_id in ongoing_processes:
            del ongoing_processes[process_id]
            
        # Check if process was successful
        if return_code != 0:
            print(f"Error enhancing image, return code: {return_code}")
            return False
            
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error enhancing image: {e}")
        if process_id in ongoing_processes:
            del ongoing_processes[process_id]
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        if process_id in ongoing_processes:
            del ongoing_processes[process_id]
        return False

def detect_objects(enhanced_image_path, detection_output_path, process_id):
    if not YOLO_AVAILABLE:
        print("YOLOv8 not available. Please install ultralytics package.")
        return False
    
    try:
        # Load YOLOv8 model
        model = YOLO(MODEL_PATH)
        
        # Run detection on enhanced image
        results = model.predict(source=enhanced_image_path, save=True, conf=0.3)
        
        # Get path to saved detection result
        result_dir = results[0].save_dir
        pred_image_path = os.path.join(result_dir, os.path.basename(enhanced_image_path))
        
        # Copy to our designated output location
        img = Image.open(pred_image_path)
        img.save(detection_output_path)
        
        return True
    except Exception as e:
        print(f"Error during object detection: {e}")
        return False

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template('index.html', error='No file selected', yolo_available=YOLO_AVAILABLE and os.path.exists(MODEL_PATH))
        
        file = request.files['file']
        if file.filename == '':
            return render_template('index.html', error='No file selected', yolo_available=YOLO_AVAILABLE and os.path.exists(MODEL_PATH))
        
        if file and allowed_file(file.filename):
            # Generate unique filename and process ID
            original_filename = secure_filename(file.filename)
            filename_base, filename_ext = os.path.splitext(original_filename)
            process_id = uuid.uuid4().hex
            filename = f"{filename_base}_{process_id[:8]}{filename_ext}"
            
            # Define paths
            input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            enhanced_path = os.path.join(app.config['ENHANCED_FOLDER'], f'enhanced_{filename}')
            detected_path = os.path.join(app.config['DETECTED_FOLDER'], f'detected_{filename}')
            
            # Save uploaded file
            file.save(input_path)
            
            # Enhance image
            if enhance_image(input_path, enhanced_path, process_id):
                # Run object detection if available
                detection_success = False
                if YOLO_AVAILABLE and os.path.exists(MODEL_PATH):
                    detection_success = detect_objects(enhanced_path, detected_path, process_id)
                
                return render_template('index.html', 
                                      original_image=url_for('uploaded_file', filename=filename),
                                      enhanced_image=url_for('enhanced_file', filename=f'enhanced_{filename}'),
                                      detected_image=url_for('detected_file', filename=f'detected_{filename}') if detection_success else None,
                                      yolo_available=YOLO_AVAILABLE and os.path.exists(MODEL_PATH))
            else:
                return render_template('index.html', error='Error enhancing image', yolo_available=YOLO_AVAILABLE and os.path.exists(MODEL_PATH))
    
    return render_template('index.html', yolo_available=YOLO_AVAILABLE and os.path.exists(MODEL_PATH))

@app.route('/cancel/<process_id>', methods=['POST'])
def cancel_process(process_id):
    """Cancel an ongoing process"""
    if process_id in ongoing_processes:
        try:
            # Terminate the process
            ongoing_processes[process_id].terminate()
            # Remove from dictionary
            del ongoing_processes[process_id]
            return jsonify({"status": "success", "message": "Process cancelled successfully"})
        except Exception as e:
            return jsonify({"status": "error", "message": f"Error cancelling process: {str(e)}"})
    else:
        return jsonify({"status": "not_found", "message": "Process not found or already completed"})

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename))

@app.route('/enhanced/<filename>')
def enhanced_file(filename):
    return send_file(os.path.join(app.config['ENHANCED_FOLDER'], filename))

@app.route('/detected/<filename>')
def detected_file(filename):
    return send_file(os.path.join(app.config['DETECTED_FOLDER'], filename))

if __name__ == '__main__':
    app.run(debug=True) 