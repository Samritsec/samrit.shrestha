from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app import db, bcrypt
from app.models.subscription import Subscription
from app.models.organization import Organization
from app.models.user import User

onboarding_bp = Blueprint("onboarding", __name__)

@onboarding_bp.route("/plan", methods=["GET"])
def plan():
    subs = Subscription.query.order_by(Subscription.price).all()
    # If you don’t have JSON features saved, show dynamic defaults safely.
    def feature_list(s):
        if isinstance(getattr(s, "features", None), list):
            return s.features
        # Fallback default features based on price
        if s.price == 0:
            return ["Basic Alerts", "Email Notifications", "Single Admin"]
        if s.price < 30:
            return ["All Basic", "Analytics & Reports", "Up to 50 Users"]
        return ["All Pro", "SIEM Integrations", "SLA Support", "Up to 500 Users"]
    enriched = [(s, feature_list(s)) for s in subs]
    return render_template("onboarding/plan.html", subscriptions=enriched)

@onboarding_bp.route("/plan", methods=["POST"])
def choose_plan():
    plan_id = request.form.get("plan_id")
    if not plan_id:
        flash("Please select a plan.", "warning")
        return redirect(url_for("onboarding.plan"))
    session["selected_plan_id"] = int(plan_id)
    return redirect(url_for("onboarding.payment"))

@onboarding_bp.route("/payment", methods=["GET", "POST"])
def payment():
    # Mock payment step (UI only). In prod connect Stripe/PayPal here.
    plan_id = session.get("selected_plan_id")
    if not plan_id:
        flash("Please select a plan first.", "warning")
        return redirect(url_for("onboarding.plan"))

    sub = Subscription.query.get(plan_id)
    if request.method == "POST":
        method = request.form.get("method")
        if method not in ("card", "paypal", "crypto"):
            flash("Select a payment method.", "warning")
            return redirect(url_for("onboarding.payment"))
        # Simulate a successful payment
        session["payment_ok"] = True
        flash("Payment authorized ✅", "success")
        return redirect(url_for("onboarding.org_setup"))

    return render_template("onboarding/payment.html", sub=sub)

@onboarding_bp.route("/org-setup", methods=["GET", "POST"])
def org_setup():
    if not session.get("selected_plan_id"):
        flash("Please select a plan first.", "warning")
        return redirect(url_for("onboarding.plan"))
    if not session.get("payment_ok"):
        flash("Please complete the payment first.", "warning")
        return redirect(url_for("onboarding.payment"))

    if request.method == "POST":
        org_name = request.form.get("org_name", "").strip()
        sector = request.form.get("sector", "").strip()
        location = request.form.get("location", "").strip()
        admin_username = request.form.get("admin_username", "").strip()
        admin_email = request.form.get("admin_email", "").strip().lower()
        pw = request.form.get("admin_password", "")
        pw2 = request.form.get("confirm_password", "")

        if not all([org_name, sector, admin_username, admin_email, pw, pw2]):
            flash("Please fill all required fields.", "warning")
            return redirect(url_for("onboarding.org_setup"))
        if pw != pw2:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("onboarding.org_setup"))
        if User.query.filter_by(email=admin_email).first():
            flash("That email is already in use.", "danger")
            return redirect(url_for("onboarding.org_setup"))

        # Create org + admin
        plan = Subscription.query.get(int(session["selected_plan_id"]))
        org = Organization(name=org_name, sector=sector or None, location=location or None, subscription_id=plan.id)
        db.session.add(org)
        db.session.flush()  # get org.id

        admin = User(
            username=admin_username,
            email=admin_email,
            role="admin",
            sector=sector or None,
            organization_id=org.id,
            subscription_id=plan.id
        )
        admin.set_password(pw)
        db.session.add(admin)
        db.session.commit()

        # Clear onboarding session flags
        session.pop("selected_plan_id", None)
        session.pop("payment_ok", None)

        flash("Organization created and admin account ready. Welcome to TenshiGuard! 🎉", "success")
        return redirect(url_for("auth.login"))

    return render_template("onboarding/org_setup.html")
