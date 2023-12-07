from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
import fitz  # PyMuPDF

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

@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(app.config['CONVERTED_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
