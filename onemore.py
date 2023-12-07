from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['CONVERTED_FOLDER'] = 'converted'

# Ensure the upload and converted folders exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['CONVERTED_FOLDER'], exist_ok=True)

def convert_document(file_path, output_format):
    # Implement the conversion logic for document files if needed
    # For now, let's just return the uploaded file path
    return file_path

@app.route('/')
def index():
    return render_template('index.html', title='EditMonk')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return redirect(request.url)

    uploaded_file = request.files['file']

    if uploaded_file.filename == '':
        return redirect(request.url)

    if uploaded_file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(uploaded_file.filename))
        uploaded_file.save(file_path)

        # Choose the conversion format based on user input
        conversion_format = request.form['format']
        if conversion_format in ['jpeg', 'png', 'webp']:
            converted_file = convert_image(file_path, conversion_format)
        elif conversion_format == 'mp3':
            converted_file = convert_audio(file_path, conversion_format)
        elif conversion_format in ['doc', 'pdf']:
            converted_file = convert_document(file_path, conversion_format)
        else:
            return render_template('error.html', title='EditMonk', message="Invalid conversion format")

        if converted_file:
            return redirect(url_for('download_file', filename=converted_file))
        else:
            return render_template('error.html', title='EditMonk', message="Error converting file")

@app.route('/upload_image', methods=['GET', 'POST'])
def upload_image():
    if request.method == 'POST':
        if 'image' not in request.files:
            return redirect(request.url)

        image = request.files['image']

        if image.filename == '':
            return redirect(request.url)

        if image:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(image.filename))
            image.save(file_path)

            # Choose the conversion format based on user input
            conversion_format = request.form['format']
            if conversion_format in ['jpeg', 'png', 'webp']:
                converted_file = convert_image(file_path, conversion_format)
            else:
                return render_template('error.html', title='EditMonk', message="Invalid conversion format")

            if converted_file:
                return redirect(url_for('download_file', filename=converted_file))
            else:
                return render_template('error.html', title='EditMonk', message="Error converting image")

    return render_template('upload_image.html', title='EditMonk')

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
                return render_template('error.html', title='EditMonk', message="Invalid conversion format")

            if converted_file:
                return redirect(url_for('download_file', filename=converted_file))
            else:
                return render_template('error.html', title='EditMonk', message="Error converting audio")

    return render_template('upload_audio.html', title='EditMonk')

@app.route('/upload_file', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)

        uploaded_file = request.files['file']

        if uploaded_file.filename == '':
            return redirect(request.url)

        if uploaded_file:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(uploaded_file.filename))
            uploaded_file.save(file_path)

            # Choose the conversion format based on user input
            conversion_format = request.form['format']
            if conversion_format in ['doc', 'pdf']:
                converted_file = convert_document(file_path, conversion_format)
            else:
                return render_template('error.html', title='EditMonk', message="Invalid conversion format")

            if converted_file:
                return redirect(url_for('download_file', filename=converted_file))
            else:
                return render_template('error.html', title='EditMonk', message="Error converting file")

    return render_template('upload_file.html', title='EditMonk')

@app.route('/download_file/<filename>')
def download_file(filename):
    return send_from_directory(app.config['CONVERTED_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
