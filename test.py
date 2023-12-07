from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
import cv2
import numpy as np

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
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)

        # Choose the conversion format based on user input
        if request.form['format'] == 'docx':
            converted_file = convert_pdf_to_docx(file_path)
        else:
            return render_template('error.html', message="Invalid conversion format")

        if converted_file:
            return redirect(url_for('download', filename=converted_file))
        else:
            return render_template('error.html', message="Error converting file")

@app.route('/upload_image', methods=['GET', 'POST'])
def upload_image():
    if request.method == 'POST':
        if 'image' not in request.files:
            return redirect(request.url)

        image = request.files['image']

        if image.filename == '':
            return redirect(request.url)

        if image:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
            image.save(file_path)

            # Choose the conversion format based on user input
            conversion_format = request.form['format']
            converted_file = convert_image(file_path, conversion_format)

            if converted_file:
                return redirect(url_for('download_image', filename=converted_file))
            else:
                return render_template('error.html', message="Error converting image")

    return render_template('upload_image.html')

@app.route('/download_image/<filename>')
def download_image(filename):
    return send_from_directory(app.config['CONVERTED_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
