from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
from pydub import AudioSegment
import cv2
import numpy as np
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['CONVERTED_FOLDER'] = 'converted'

# Ensure the upload and converted folders exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['CONVERTED_FOLDER'], exist_ok=True)

def convert_image(file_path, output_format):
    try:
        # Read the image using OpenCV
        image = cv2.imread(file_path)

        # Convert the image to the desired format
        _, buffer = cv2.imencode(f".{output_format}", image)
        converted_file_path = os.path.join(app.config['CONVERTED_FOLDER'], f'converted.{output_format}')
        with open(converted_file_path, 'wb') as image_file:
            image_file.write(buffer)

        return f'converted.{output_format}'
    except Exception as e:
        print(f"Error converting image: {e}")
        return None

def convert_audio(file_path, output_format):
    try:
        # Read the audio using pydub
        audio = AudioSegment.from_file(file_path)

        # Convert the audio to MP3
        if output_format == 'mp3':
            converted_file_path = os.path.join(app.config['CONVERTED_FOLDER'], 'converted.mp3')
            audio.export(converted_file_path, format='mp3')
            return 'converted.mp3'
        else:
            raise ValueError(f"Unsupported audio format: {output_format}")

    except Exception as e:
        print(f"Error converting audio: {e}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return redirect(request.url)

    file = request.files['file']

    if file.filename == '':
        return redirect(request.url)

    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename))
        file.save(file_path)

        # Choose the conversion format based on user input
        conversion_format = request.form['format']
        if conversion_format in ['jpeg', 'png', 'webp']:
            converted_file = convert_image(file_path, conversion_format)
        else:
            return render_template('error.html', message="Invalid conversion format")

        if converted_file:
            return redirect(url_for('download_image', filename=converted_file))
        else:
            return render_template('error.html', message="Error converting image")

@app.route('/upload_audio', methods=['GET', 'POST'])
def upload_audio():
    if request.method == 'POST':
        if 'audio' not in request.files:
            return redirect(request.url)

        audio = request.files['audio']

        if audio.filename == '':
            return redirect(request.url)

        if audio:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(audio.filename))
            audio.save(file_path)

            # Choose the conversion format based on user input
            conversion_format = request.form['format']
            if conversion_format == 'mp3':
                converted_file = convert_audio(file_path, conversion_format)
            else:
                return render_template('error.html', message="Invalid conversion format")

            if converted_file:
                return redirect(url_for('download_audio', filename=converted_file))
            else:
                return render_template('error.html', message="Error converting audio")

    return render_template('upload_audio.html')

@app.route('/download_image/<filename>')
def download_image(filename):
    return send_from_directory(app.config['CONVERTED_FOLDER'], filename, as_attachment=True)

@app.route('/download_audio/<filename>')
def download_audio(filename):
    return send_from_directory(app.config['CONVERTED_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
