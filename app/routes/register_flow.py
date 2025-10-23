from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.exceptions import abort
from app import db
from app.models.subscription import Subscription
from app.models.organization import Organization
from app.models.user import User
from app.models.alerting import AlertPreference, ALERT_TYPES
from app.models.alerting import NotificationChannel



register_flow = Blueprint("register_flow", __name__, url_prefix="/register")


# =========================================================
# 🔸 Helper: Check required session keys
# =========================================================
def _require(keys):
    for k in keys:
        if session.get(k) is None:
            return False
    return True


# =========================================================
# 🔹 Step 1: Organization Registration
# =========================================================
@register_flow.route("/org", methods=["GET"])
def org():
    """Show the organization registration form."""
    return render_template("register/step1_org.html")


@register_flow.route("/org", methods=["POST"])
def org_submit():
    """Handle organization registration form submission."""
    org_name = request.form.get("org_name", "").strip()
    sector = request.form.get("sector", "").strip()
    location = request.form.get("location", "").strip()

    if not org_name or not sector:
        flash("Please provide Organization Name and Sector.", "danger")
        return redirect(url_for("register_flow.org"))

    # Prevent duplicates
    existing = Organization.query.filter_by(name=org_name).first()
    if existing:
        flash("This organization already exists. Please choose another name.", "warning")
        return redirect(url_for("register_flow.org"))

    org = Organization(
        name=org_name,
        sector=sector,
        location=location,
        is_paid=False,
        status="lead",
        total_users=0,
        total_devices=0,
        subscription_id=None,
    )

    db.session.add(org)
    db.session.commit()

    session["org_id"] = org.id
    session["org_info"] = {
        "org_name": org_name,
        "sector": sector,
        "location": location,
    }

    return redirect(url_for("register_flow.plan"))


# =========================================================
# 🔹 Step 2: Subscription Plan Selection
# =========================================================
@register_flow.route("/plan", methods=["GET"])
def plan():
    """Show the available subscription plans."""
    if not session.get("org_id"):
        flash("Please register your organization first.", "warning")
        return redirect(url_for("register_flow.org"))

    # Static plan catalog (later can move to DB)
    plans = [
        {
            "id": 1,
            "name": "Basic",
            "price": 29,
            "max_users": 3,
            "max_devices": 5,
            "features": [
                "Basic endpoint monitoring",
                "Email alerts only",
                "No AI threat detection",
            ],
        },
        {
            "id": 2,
            "name": "Professional",
            "price": 79,
            "max_users": 10,
            "max_devices": 20,
            "features": [
                "Advanced reporting dashboard",
                "Custom alert rules",
                "Email & SMS alerts",
                "Critical phone-call alerts (SOS)",
            ],
        },
        {
            "id": 3,
            "name": "Enterprise",
            "price": 199,
            "max_users": None,
            "max_devices": None,
            "features": [
                "Unlimited users & devices",
                "AI-based analytics",
                "Role-based access control",
                "24/7 priority response",
                "SOS voice-call alerts",
            ],
        },
    ]

    return render_template("register/step2_plan.html", plans=plans)


@register_flow.route("/plan", methods=["POST"])
def select_plan():
    """Save the user's plan choice and move to payment."""
    if not session.get("org_id"):
        return redirect(url_for("register_flow.org"))

    plan_id = request.form.get("plan_id")
    try:
        plan_id = int(plan_id)
    except Exception:
        flash("Invalid plan selected.", "danger")
        return redirect(url_for("register_flow.plan"))

    plan_map = {
        1: {"name": "Basic", "price": 29},
        2: {"name": "Professional", "price": 79},
        3: {"name": "Enterprise", "price": 199},
    }

    if plan_id not in plan_map:
        flash("Invalid plan ID.", "danger")
        return redirect(url_for("register_flow.plan"))

    session["selected_plan_id"] = plan_id
    session["selected_plan"] = plan_map[plan_id]

    flash(f"Selected {plan_map[plan_id]['name']} Plan.", "info")
    return redirect(url_for("register_flow.payment"))


# =========================================================
# 🔹 Step 3: Payment (Mock)
# =========================================================
@register_flow.route("/payment", methods=["GET", "POST"])
def payment():
    """Mock payment gateway."""
    if not _require(["org_id", "selected_plan"]):
        flash("Please complete previous steps first.", "warning")
        return redirect(url_for("register_flow.org"))

    selected_plan = session["selected_plan"]

    if request.method == "POST":
        method = request.form.get("payment_method", "").strip()
        if method not in ("Credit Card", "PayPal", "Crypto"):
            flash("Please choose a valid payment method.", "danger")
            return redirect(url_for("register_flow.payment"))

        # Mock success
        session["payment_ok"] = True
        flash("✅ Payment successful! Let's create your admin account.", "success")
        return redirect(url_for("register_flow.admin"))

    return render_template("register/step3_payment.html", selected_plan=selected_plan)


# =========================================================
# 🔹 Step 4: Admin Account Creation + Alert Preferences
# =========================================================
@register_flow.route("/admin", methods=["GET"])
def admin():
    """Display admin setup + alert configuration."""
    if not _require(["org_id", "payment_ok", "selected_plan_id"]):
        flash("Please complete payment first.", "warning")
        return redirect(url_for("register_flow.payment"))

    plan_id = session["selected_plan_id"]

    # Default alerts per plan
    if plan_id == 1:  # Basic
        defaults = dict(
            enabled_types=["suspicious_login"],
            voice_call_on_critical=False,
        )
    elif plan_id == 2:  # Professional
        defaults = dict(
            enabled_types=["bruteforce", "suspicious_login"],
            voice_call_on_critical=True,
        )
    else:  # Enterprise
        defaults = dict(
            enabled_types=[
                "bruteforce",
                "unregistered_device",
                "malware",
                "data_exfil",
                "suspicious_login",
            ],
            voice_call_on_critical=True,
        )

    return render_template(
        "register/step4_admin.html",
        alert_types=list(ALERT_TYPES),
        defaults=defaults,
        plan_name=session["selected_plan"]["name"],
    )


@register_flow.route("/admin", methods=["POST"])
def admin_submit():
    """Create admin user + save alert preferences."""
    if not _require(["org_id", "payment_ok", "selected_plan_id"]):
        return redirect(url_for("register_flow.payment"))

    org = Organization.query.get(session["org_id"])
    if not org:
        abort(400, "Organization not found")

    username = request.form.get("username", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    confirm = request.form.get("confirm_password", "")
    alert_email = request.form.get("alert_email", "").strip().lower()
    alert_phone = request.form.get("alert_phone", "").strip()
    selected_alerts = request.form.getlist("enabled_types")
    voice_toggle = request.form.get("voice_call_on_critical") == "on"

    if not all([username, email, password, confirm]):
        flash("Please fill all required admin fields.", "danger")
        return redirect(url_for("register_flow.admin"))

    if password != confirm:
        flash("Passwords do not match.", "danger")
        return redirect(url_for("register_flow.admin"))

    # Finalize organization
    org.is_paid = True
    org.status = "active"
    org.subscription_id = session["selected_plan_id"]
    db.session.add(org)

    # Create admin
    admin_user = User(
        username=username,
        email=email,
        role="admin",
        sector=org.sector,
        organization_id=org.id,
        subscription_id=org.subscription_id,
    )
    admin_user.set_password(password)
    db.session.add(admin_user)
    db.session.flush()

    # Sanitize alert types
    cleaned = [t for t in selected_alerts if t in ALERT_TYPES]

    # Alert Preferences
    pref = AlertPreference(
        organization_id=org.id,
        enabled_types=cleaned,
        voice_call_on_critical=voice_toggle,
    )
    db.session.add(pref)
    db.session.flush()

    # Notification Channels
    db.session.add(
        NotificationChannel(
            organization_id=org.id,
            kind="email",
            value=(alert_email or email),
            is_primary=True,
        )
    )
    if alert_phone:
        db.session.add(
            NotificationChannel(
                organization_id=org.id,
                kind="voice",
                value=alert_phone,
                is_primary=True,
            )
        )

    db.session.commit()

    # Cleanup session
    for k in ["org_id", "org_info", "selected_plan_id", "selected_plan", "payment_ok"]:
        session.pop(k, None)

    # Show success animation page instead of redirect
    return render_template("register/success.html", org=org)
