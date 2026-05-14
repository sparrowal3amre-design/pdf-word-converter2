from flask import Flask, render_template, request, send_file
from pdf2docx import Converter
from werkzeug.utils import secure_filename
import subprocess
import os

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

    filepath = os.path.join(
        UPLOAD_FOLDER,
        filename
    )

    file.save(filepath)

    if mode == "pdf_to_word":

        output_path = filepath.replace(
            ".pdf",
            ".docx"
        )

        cv = Converter(filepath)
        cv.convert(output_path)
        cv.close()

        return send_file(
            output_path,
            as_attachment=True
        )

    elif mode == "word_to_pdf":

        output_path = filepath.replace(
            ".docx",
            ".pdf"
        )

        subprocess.run([
            "libreoffice",
            "--headless",
            "--convert-to",
            "pdf",
            filepath,
            "--outdir",
            UPLOAD_FOLDER
        ])

        return send_file(
            output_path,
            as_attachment=True
        )

    return "Invalid mode"

if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            5000
        )
    )

    app.run(
        host="0.0.0.0",
        port=port
    )
