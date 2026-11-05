import os
import tempfile
from flask import Flask, request, redirect, url_for, render_template_string
from werkzeug.utils import secure_filename
from app.s3_service import S3Service
from app.db import init_db, save_report, get_reports

app = Flask(__name__)
s3_service = S3Service()

HTML_TEMPLATE = """
<!doctype html>
<html>
<head><title>CloudVault Pilot</title></head>
<body style="font-family: monospace; max-width: 800px; margin: 40px auto;">
    <h2>🛡️ CloudVault Pilot — S3 + RDS Audit Log</h2>
    <form action="/upload" method="post" enctype="multipart/form-data">
        <input type="file" name="file" required>
        <button type="submit">Subir a S3 y Registrar en DB</button>
    </form>
    <hr>
    <h3>Archivos Registrados en PostgreSQL:</h3>
    <table border="1" cellpadding="6" style="border-collapse: collapse; width: 100%;">
        <tr><th>ID</th><th>Archivo</th><th>SHA-256 (Primeros 16 chars)</th><th>Fecha</th><th>Acción</th></tr>
        {% for r in reports %}
        <tr>
            <td>{{ r.id }}</td>
            <td>{{ r.filename }}</td>
            <td>{{ r.sha256[:16] }}...</td>
            <td>{{ r.created_at }}</td>
            <td><a href="{{ r.s3_url }}" target="_blank">Descargar de S3</a></td>
        </tr>
        {% endfor %}
    </table>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def index():
    init_db()
    reports = get_reports()
    return render_template_string(HTML_TEMPLATE, reports=reports)

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("file")
    if not file or file.filename == "":
        return "Archivo inválido", 400
    filename = secure_filename(file.filename)
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        file.save(tmp.name)
        res = s3_service.upload_file_and_get_url(tmp.name, filename)
        os.unlink(tmp.name)
    save_report(filename, res["sha256"], res["url"])
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
