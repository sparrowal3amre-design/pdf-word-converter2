from flask import Flask, render_template, request, send_file
from pdf2docx import Converter
from werkzeug.utils import secure_filename
from docx2pdf import convert
import os
import shutil

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

    # حفظ الملف المرفوع
    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)
    
    output_path = None
    
    try:
        # التحويل من PDF إلى Word
        if mode == "pdf_to_word":
            if not filename.lower().endswith('.pdf'):
                return "File must be PDF for this conversion"
            
            output_path = filepath.replace('.pdf', '.docx')
            cv = Converter(filepath)
            cv.convert(output_path)
            cv.close()
        
        # التحويل من Word إلى PDF
        elif mode == "word_to_pdf":
            if not filename.lower().endswith('.docx'):
                return "File must be DOCX for this conversion"
            
            output_path = filepath.replace('.docx', '.pdf')
            convert(filepath, output_path)
        
        else:
            return "Invalid mode"
        
        # التحقق من وجود ملف الإخراج
        if not os.path.exists(output_path):
            return "Conversion failed - output file not created"
        
        # إرسال الملف المحول
        return send_file(
            output_path,
            as_attachment=True,
            download_name=os.path.basename(output_path)
        )
    
    except Exception as e:
        return f"Error during conversion: {str(e)}"
    
    finally:
        # تنظيف الملفات المؤقتة (اختياري - حذف الملف الأصلي)
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
            except:
                pass
        
        # حذف ملف الإخراج بعد إرساله (للحفاظ على المساحة)
        if output_path and os.path.exists(output_path):
            try:
                os.remove(output_path)
            except:
                pass

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
