from flask import Blueprint, jsonify, request, send_file
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import csv
from app import db
from app.models.user import User
from app.models.device import Device
from app.models.organization import Organization

api_bp = Blueprint("api_bp", __name__, url_prefix="/api")

# -------------------------
# Add User
# -------------------------
@api_bp.route("/add-user", methods=["POST"])
def add_user():
    data = request.get_json()
    try:
        org = Organization.query.first()
        if not org:
            return jsonify({"success": False, "error": "No organization found."}), 400

        new_user = User(
            username=data["username"],
            email=data["email"],
            role=data.get("role", "user"),
            organization_id=org.id,
            password_hash=data["password"],  # For simplicity (replace with hash later)
        )
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


# -------------------------
# Add Device
# -------------------------
@api_bp.route("/add-device", methods=["POST"])
def add_device():
    data = request.get_json()
    try:
        org = Organization.query.first()
        new_device = Device(
            hostname=data["hostname"],
            os=data["os"],
            ip=data["ip"],
            organization_id=org.id,
            status="online",
            cpu=0,
            mem=0,
        )
        db.session.add(new_device)
        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


# -------------------------
# Add Agent
# -------------------------
@api_bp.route("/add-agent", methods=["POST"])
def add_agent():
    data = request.get_json()
    try:
        org = Organization.query.first()
        new_agent = Device(
            hostname=data["agent_name"],
            os=data.get("agent_type", "Linux"),
            ip="127.0.0.1",
            organization_id=org.id,
            status="online",
            cpu=1,
            mem=1,
        )
        db.session.add(new_agent)
        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


# -------------------------
# Generate Report
# -------------------------
@api_bp.route("/generate-report")
def generate_report():
    report_type = request.args.get("type", "summary")

    if report_type == "summary":
        # Create CSV
        output = BytesIO()
        writer = csv.writer(output)
        writer.writerow(["Host", "OS", "IP", "Status", "CPU%", "Mem%"])
        for d in Device.query.all():
            writer.writerow([d.hostname, d.os, d.ip, d.status, d.cpu, d.mem])
        output.seek(0)
        return send_file(
            output,
            mimetype="text/csv",
            as_attachment=True,
            download_name="tenshiguard-summary.csv",
        )

    else:
        # Create PDF
        buffer = BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=letter)
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(100, 750, "TenshiGuard Security Report")
        pdf.setFont("Helvetica", 10)
        y = 720
        for dev in Device.query.all():
            pdf.drawString(80, y, f"{dev.hostname} ({dev.os}) - {dev.status}")
            y -= 20
        pdf.save()
        buffer.seek(0)
        return send_file(
            buffer,
            as_attachment=True,
            download_name="tenshiguard-report.pdf",
            mimetype="application/pdf",
        )
