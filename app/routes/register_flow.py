# app/routes/register_flow.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.exceptions import abort
from flask_login import login_user
from app.extensions import db
from app.models.organization import Organization
from app.models.user import User
from app.models.alerting import AlertPreference, ALERT_TYPES, NotificationChannel
from app.config.plans import PLAN_CATALOG, plan_for_id

register_flow = Blueprint("register_flow", __name__, url_prefix="/register")

def _require(keys):
    return all(session.get(k) is not None for k in keys)

# ---------------------------
# STEP 1: Organization details
# ---------------------------
@register_flow.route("/org", methods=["GET", "POST"], endpoint="org")
def org_submit():
    if request.method == "POST":
        org_name = (request.form.get("org_name") or "").strip()
        sector   = (request.form.get("sector") or "").strip().lower()
        email    = (request.form.get("email") or "").strip().lower()
        password = (request.form.get("password") or "")

        if not org_name or not sector or not email or not password:
            flash("Please fill in all fields.", "warning")
            return redirect(url_for("register_flow.org"))

        # Prevent duplicates
        existing_org = Organization.query.filter_by(name=org_name).first()
        if existing_org:
            flash("Organization already registered.", "warning")
            return redirect(url_for("register_flow.org"))

        # Create org (pending until payment)
        org = Organization(
            name=org_name,
            sector=sector,
            status="pending",
            is_paid=False,
        )
        db.session.add(org)
        db.session.commit()

        # Stash minimal info for later steps (no user yet)
        session["org_id"] = org.id
        session["org_sector"] = org.sector
        session["admin_email_prefill"] = email
        session["admin_password_prefill"] = password

        return redirect(url_for("register_flow.plan"))

    return render_template("register/step1_org.html")

# ---------------------------
# STEP 2: Plan selection
# ---------------------------
@register_flow.route("/plan", methods=["GET", "POST"])
def plan():
    if request.method == "POST":
        plan_id = request.form.get("plan_id")
        try:
            plan_id = int(plan_id)
        except Exception:
            flash("Please choose a valid plan.", "danger")
            return redirect(url_for("register_flow.plan"))

        plan = plan_for_id(plan_id)
        if not plan:
            flash("Invalid plan selected.", "danger")
            return redirect(url_for("register_flow.plan"))

        session["selected_plan_id"] = plan_id
        flash(f"Selected {plan['name']} plan.", "info")
        return redirect(url_for("register_flow.payment"))

    return render_template("register/step2_plan.html", plans=PLAN_CATALOG)

# ---------------------------
# STEP 3: Mock payment
# ---------------------------
@register_flow.route("/payment", methods=["GET", "POST"])
def payment():
    if not _require(["org_id", "selected_plan_id"]):
        flash("Please complete previous steps first.", "warning")
        return redirect(url_for("register_flow.org"))

    plan = plan_for_id(session["selected_plan_id"])

    if request.method == "POST":
        method = (request.form.get("payment_method") or "").strip()
        if method not in ("Credit Card", "PayPal", "Crypto"):
            flash("Choose a valid payment method.", "danger")
            return redirect(url_for("register_flow.payment"))

        session["payment_ok"] = True
        flash("✅ Payment successful! Now create your admin account.", "success")
        return redirect(url_for("register_flow.admin"))

    return render_template("register/step3_payment.html", plan=plan)

# ---------------------------
# STEP 4: Admin setup + alerts
# ---------------------------
@register_flow.route("/admin", methods=["GET", "POST"])
def admin():
    if not _require(["org_id", "selected_plan_id", "payment_ok"]):
        flash("Please finish payment first.", "warning")
        return redirect(url_for("register_flow.payment"))

    plan = plan_for_id(session["selected_plan_id"])
    org = Organization.query.get(session["org_id"])
    if not org:
        abort(400, "Organization not found")

    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        email    = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""
        confirm  = request.form.get("confirm_password") or ""

        alert_email = (request.form.get("alert_email") or email).strip().lower()
        alert_phone = (request.form.get("alert_phone") or "").strip()

        selected_alerts = request.form.getlist("enabled_types")

        # Gate voice calls/SOS by plan
        voice_toggle = (request.form.get("voice_call_on_critical") == "on")
        if not plan["supports_sos_voice"]:
            voice_toggle = False

        if not username or not email or not password or not confirm:
            flash("Please fill all required fields.", "danger")
            return redirect(url_for("register_flow.admin"))

        if password != confirm:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("register_flow.admin"))

        # Finalize org
        org.subscription_id = plan["id"]
        org.is_paid = True
        org.status  = "active"
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

        # Save alert preferences
        pref = AlertPreference(
            organization_id=org.id,
            enabled_types=cleaned,
            voice_call_on_critical=voice_toggle,
        )
        db.session.add(pref)

        # Notification channels
        db.session.add(NotificationChannel(
            organization_id=org.id,
            kind="email",
            value=alert_email,
            is_primary=True,
        ))

        # Only add phone if non-empty and plan allows voice SOS
        if alert_phone and plan["supports_sos_voice"]:
            db.session.add(NotificationChannel(
                organization_id=org.id,
                kind="voice",
                value=alert_phone,
                is_primary=True,
            ))

        db.session.commit()

        # Auto-login and go to the correct sector
        login_user(admin_user)
        # Clean up session
        for k in ["org_id", "org_sector", "admin_email_prefill", "admin_password_prefill",
                  "selected_plan_id", "payment_ok"]:
            session.pop(k, None)

        return render_template("register/success.html", org=org, plan=plan)

    # GET: defaults
    defaults = {
        "email": session.get("admin_email_prefill", ""),
        "password": session.get("admin_password_prefill", ""),
        "voice_allowed": plan["supports_sos_voice"],
    }
    return render_template(
        "register/step4_admin.html",
        alert_types=list(ALERT_TYPES),
        plan=plan,
        org=org,
        defaults=defaults,
    )
