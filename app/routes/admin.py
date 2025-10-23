from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app.models.organization import Organization
from app.models.user import User
from app.models.security_event import SecurityEvent

bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.before_request
def restrict_to_admins():
    if not current_user.is_authenticated or not current_user.is_admin():
        return redirect(url_for('auth.login'))

@bp.route('/')
@login_required
def dashboard():
    organizations = Organization.query.all()
    users = User.query.all()
    recent_events = SecurityEvent.query.order_by(SecurityEvent.timestamp.desc()).limit(10).all()

    return render_template(
        'admin_dashboard.html',
        organizations=organizations,
        users=users,
        events=recent_events
    )
