from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db, bcrypt
from app.models.organization import Organization
from app.models.user import User
from app.models.subscription import Subscription
from flask_login import login_user

register_org_bp = Blueprint("register_org", __name__, url_prefix="/register-org")


@register_org_bp.route("/", methods=["GET", "POST"])
def register_org():
    """Organization + Admin registration route"""
    subscriptions = Subscription.query.all()  # For dropdown

    if request.method == "POST":
        org_name = request.form.get("org_name")
        sector = request.form.get("sector")
        location = request.form.get("location")
        plan_id = request.form.get("subscription_id")

        admin_username = request.form.get("admin_username")
        admin_email = request.form.get("admin_email")
        admin_password = request.form.get("admin_password")
        confirm_password = request.form.get("confirm_password")

        # --- Validation ---
        if admin_password != confirm_password:
            flash("Passwords do not match!", "danger")
            return render_template("register_org.html", subscriptions=subscriptions)

        if User.query.filter_by(email=admin_email).first():
            flash("Email already registered!", "warning")
            return render_template("register_org.html", subscriptions=subscriptions)

        try:
            # --- Create organization ---
            org = Organization(
                name=org_name,
                sector=sector,
                location=location,
                subscription_id=plan_id,
                total_users=1,
                total_devices=0
            )
            db.session.add(org)
            db.session.flush()  # gives org.id

            # --- Create admin user ---
            hashed_pw = bcrypt.generate_password_hash(admin_password).decode("utf-8")
            admin_user = User(
                username=admin_username,
                email=admin_email,
                password_hash=hashed_pw,
                role="admin",
                organization_id=org.id,
                subscription_id=plan_id,
                sector=sector
            )
            db.session.add(admin_user)
            db.session.commit()

            # --- Log in newly created admin ---
            login_user(admin_user)
            flash("Organization and admin registered successfully!", "success")
            return redirect(url_for("dashboard.org_admin_dashboard"))

        except Exception as e:
            db.session.rollback()
            flash(f"Registration failed: {str(e)}", "danger")

    return render_template("register_org.html", subscriptions=subscriptions)
