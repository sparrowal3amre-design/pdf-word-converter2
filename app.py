from flask import Flask, render_template, request, send_file
from pdf2docx import Converter
from werkzeug.utils import secure_filename
import os
import subprocess
import sys

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/convert", methods=["POST"])
def convert_file():
    if "file" not in request.files:
        return "No file uploaded"

    file = request.files["file"]
    mode = request.form.get("mode")

    if file.filename == "":
        return "No selected file"

    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)
    
    try:
        if mode == "pdf_to_word":
            # التحويل من PDF إلى Word
            if not filename.lower().endswith('.pdf'):
                return "File must be PDF format"
            
            output_path = filepath.replace('.pdf', '.docx')
            cv = Converter(filepath)
            cv.convert(output_path)
            cv.close()
            
            return send_file(output_path, as_attachment=True)
        
        elif mode == "word_to_pdf":
            # التحويل من Word إلى PDF
            if not filename.lower().endswith('.docx'):
                return "File must be DOCX format"
            
            output_path = filepath.replace('.docx', '.pdf')
            
            # استخدام python-docx2pdf كحل بديل (يعمل بدون LibreOffice)
            try:
                from docx2pdf import convert
                convert(filepath, output_path)
            except ImportError:
                # إذا لم تكن docx2pdf مثبتة، نحاول استخدام LibreOffice
                try:
                    result = subprocess.run([
                        "libreoffice",
                        "--headless",
                        "--convert-to",
                        "pdf",
                        "--outdir",
                        UPLOAD_FOLDER,
                        filepath
                    ], capture_output=True, text=True)
                    
                    if result.returncode != 0:
                        return f"Conversion failed: {result.stderr}"
                except FileNotFoundError:
                    return "Please install docx2pdf (pip install docx2pdf) or install LibreOffice"
            
            # التحقق من وجود ملف الإخراج
            if os.path.exists(output_path):
                return send_file(output_path, as_attachment=True)
            else:
                return "PDF file was not created"
        
        else:
            return "Invalid mode"
    
    except Exception as e:
        return f"Error: {str(e)}"
    
    finally:
        # حذف الملف الأصلي بعد التحويل
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
            except:
                pass

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
