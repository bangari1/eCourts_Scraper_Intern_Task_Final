from flask import Flask, render_template, request, jsonify, send_file
import json, io, os
from bs4 import BeautifulSoup
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime

app = Flask(__name__)
os.makedirs("results", exist_ok=True)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/get_data", methods=["GET"])
def get_data():
    with open("static/courts.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    return jsonify(data)

@app.route("/download", methods=["POST"])
def download():
    state = request.form.get("state")
    district = request.form.get("district")
    complex_name = request.form.get("complex")
    court = request.form.get("court")
    date = request.form.get("date")

    # --- Simulated HTML cause list ---
    html = f"""
    <table border="1">
      <tr><th>Case No.</th><th>Parties</th><th>Status</th></tr>
      <tr><td>1234/2024</td><td>ABC vs XYZ</td><td>For Hearing</td></tr>
      <tr><td>5678/2024</td><td>PQR vs LMN</td><td>For Orders</td></tr>
    </table>
    """

    # --- Convert to PDF ---
    pdf_buffer = io.BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = [
        Paragraph("<b>eCourts Cause List (Demo)</b>", styles["Title"]),
        Spacer(1, 12),
        Paragraph(f"State: {state}", styles["Normal"]),
        Paragraph(f"District: {district}", styles["Normal"]),
        Paragraph(f"Court Complex: {complex_name}", styles["Normal"]),
        Paragraph(f"Court: {court or 'All'}", styles["Normal"]),
        Paragraph(f"Date: {date}", styles["Normal"]),
        Spacer(1, 12)
    ]
    soup = BeautifulSoup(html, "html.parser")
    for tr in soup.find_all("tr"):
        text = " | ".join(td.get_text(strip=True) for td in tr.find_all(["td", "th"]))
        if text:
            story.append(Paragraph(text, styles["Normal"]))
    doc.build(story)

    pdf_buffer.seek(0)
    filename = f"CauseList_{date.replace('-', '_')}.pdf"
    return send_file(pdf_buffer, as_attachment=True,
                     download_name=filename, mimetype="application/pdf")

if __name__ == "__main__":
    app.run(debug=True, port=5000)
