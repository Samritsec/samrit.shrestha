from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required
from app import db, bcrypt, mail
from app.models.user import User
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadTimeSignature
from config import Config

auth = Blueprint("auth", __name__, url_prefix="/")

# =========================================================
# Helper: Token Serializer
# =========================================================
def generate_token(email):
    """Generate a signed token for password reset links."""
    s = URLSafeTimedSerializer(Config.SECRET_KEY)
    return s.dumps(email, salt="password-reset")


def verify_token(token, expiration=3600):
    """Validate a reset token and return the embedded email if valid."""
    s = URLSafeTimedSerializer(Config.SECRET_KEY)
    try:
        email = s.loads(token, salt="password-reset", max_age=expiration)
        return email
    except (SignatureExpired, BadTimeSignature):
        return None


# =========================================================
# LOGIN
# =========================================================
@auth.route("/login", methods=["GET", "POST"])
def login():
    """Handle login for all users (Admin / Normal)."""
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        # Find user
        user = User.query.filter_by(email=email).first()
        if not user or not bcrypt.check_password_hash(user.password_hash, password):
            flash("Invalid email or password.", "danger")
            return render_template("auth/login.html")

        # Successful login
        login_user(user)
        flash(f"Welcome back, {user.username}!", "success")

        # Route by role
        if user.role == "admin":
            return redirect(url_for("dashboard.admin_dashboard"))
        else:
            return redirect(url_for("dashboard.user_dashboard"))

    return render_template("auth/login.html")


# =========================================================
# LOGOUT
# =========================================================
@auth.route("/logout")
@login_required
def logout():
    """Log out the current user and redirect to login."""
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))


# =========================================================
# FORGOT PASSWORD
# =========================================================
@auth.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    """Allow users to request a password reset email."""
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        user = User.query.filter_by(email=email).first()

        if not user:
            flash("Email not found in our records.", "danger")
            return render_template("auth/forgot_password.html")

        # Generate secure token
        token = generate_token(user.email)
        reset_url = url_for("auth.reset_password", token=token, _external=True)

        # Compose message
        msg = Message(
            subject="🔐 TenshiGuard Password Reset",
            sender=Config.MAIL_DEFAULT_SENDER,
            recipients=[user.email],
            body=f"""
Hello {user.username},

We received a request to reset your TenshiGuard account password.
Click the link below to set a new password (valid for 1 hour):

{reset_url}

If you didn’t request this, please ignore this email.

— The TenshiGuard Team
""",
        )

        try:
            mail.send(msg)
            flash("✅ Password reset link sent to your email.", "success")
        except Exception as e:
            print(f"[Mail Error] {e}")
            flash("⚠️ Could not send email. Check mail configuration.", "danger")

        return redirect(url_for("auth.login"))

    return render_template("auth/forgot_password.html")


# =========================================================
# RESET PASSWORD
# =========================================================
@auth.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    """Handle password reset from emailed token."""
    email = verify_token(token)
    if not email:
        flash("Invalid or expired reset link. Please try again.", "danger")
        return redirect(url_for("auth.forgot_password"))

    if request.method == "POST":
        password = request.form.get("password", "")
        confirm = request.form.get("confirm", "")

        if password != confirm:
            flash("Passwords do not match.", "danger")
            return render_template("auth/reset_password.html", token=token)

        user = User.query.filter_by(email=email).first()
        if not user:
            flash("User not found.", "danger")
            return redirect(url_for("auth.login"))

        user.set_password(password)
        db.session.commit()
        flash("✅ Password updated successfully! You can now log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/reset_password.html", token=token)
