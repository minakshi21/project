from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
from pydub import AudioSegment
import cv2
from werkzeug.utils import secure_filename
import fitz
import docx2pdf  # Added import for docx2pdf

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['CONVERTED_FOLDER'] = 'converted'

# Ensure the upload and converted folders exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['CONVERTED_FOLDER'], exist_ok=True)

def convert_pdf_to_docx(file_path):
    try:
        pdf_document = fitz.open(file_path)
        text = ""
        for page_number in range(pdf_document.page_count):
            page = pdf_document.load_page(page_number)
            text += page.get_text()

        converted_file_path = os.path.join(app.config['CONVERTED_FOLDER'], 'converted.docx')
        with open(converted_file_path, 'w', encoding='utf-8') as docx_file:
            docx_file.write(text)

        return 'converted.docx'
    except Exception as e:
        print(f"Error converting PDF to DOCX: {e}")
        return None

def convert_docx_to_pdf(file_path, output_format):
    try:
        if output_format == 'pdf':
            # Convert DOCX to PDF using docx2pdf
            converted_file_path = os.path.join(app.config['CONVERTED_FOLDER'], 'converted.pdf')
            docx2pdf.convert(file_path, converted_file_path)
            return 'converted.pdf'
        elif output_format == 'doc':
            # Add logic to convert PDF to DOCX (you may need to choose an appropriate library)
            # For example, you can use PyMuPDF (fitz) to convert PDF to DOCX
            return convert_pdf_to_docx(file_path)
        else:
            raise ValueError(f"Unsupported document format: {output_format}")

    except Exception as e:
        print(f"Error converting document: {e}")
        return None

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
    return render_template('index.html', title='EditMonk')

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
            if conversion_format in ['docx','doc', 'pdf']:
                # Use the appropriate conversion function based on the format
                converted_file = convert_docx_to_pdf(file_path, conversion_format)
            else:
                return render_template('error.html', title='EditMonk', message="Invalid conversion format")

            if converted_file:
                return redirect(url_for('download_file', filename=converted_file))
            else:
                return render_template('error.html', title='Error', message="Error converting file")

    return render_template('upload_file.html', title='EditMonk')

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
        if conversion_format in ['jpg','jpeg', 'png', 'webp']:
            converted_file = convert_image(file_path, conversion_format)
        else:
            return render_template('error.html', title='EditMonk', message="Invalid conversion format")

        if converted_file:
            return redirect(url_for('download_image', filename=converted_file))
        else:
            return render_template('error.html', title='EditMonk', message="Error converting image")

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
                return redirect(url_for('download_audio', filename=converted_file))
            else:
                return render_template('error.html', title='EditMonk', message="Error converting audio")

    return render_template('upload_audio.html', title='EditMonk')

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
                return redirect(url_for('download_image', filename=converted_file))
            else:
                return render_template('error.html', title='EditMonk', message="Error converting image")

    return render_template('upload_image.html', title='EditMonk')

@app.route('/download_image/<filename>')
def download_image(filename):
    return send_from_directory(app.config['CONVERTED_FOLDER'], filename, as_attachment=True)

@app.route('/download_audio/<filename>')
def download_audio(filename):
    return send_from_directory(app.config['CONVERTED_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
