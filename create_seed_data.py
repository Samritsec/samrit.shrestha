# create_seed_data.py
from app import create_app, db
from app.models.subscription import Subscription
from app.models.organization import Organization
from app.models.user import User

app = create_app()

# =========================================================
# 🚀 Seed Script: TenshiGuard Default Data
# =========================================================
def seed_subscriptions():
    """Creates or updates the 3 main subscription tiers."""

    plans = [
        {
            "name": "Basic",
            "description": "Perfect for small teams that need basic endpoint monitoring and reporting.",
            "price": 0.0,
            "billing_cycle": "monthly",
            "max_users": 5,
            "max_devices": 10,
            "alert_type": "none",
            "features": [
                "Basic dashboard access",
                "Device activity overview",
                "Email-only login alerts",
                "Community support"
            ],
        },
        {
            "name": "Professional",
            "description": "Ideal for growing organizations needing proactive security alerts and detailed analytics.",
            "price": 29.99,
            "billing_cycle": "monthly",
            "max_users": 20,
            "max_devices": 40,
            "alert_type": "email_sms",
            "features": [
                "All Basic features",
                "Bruteforce detection alerts (email + SMS)",
                "User behavior analytics",
                "Scheduled security reports",
                "24/7 email support"
            ],
        },
        {
            "name": "Enterprise",
            "description": "Complete enterprise-grade monitoring with custom alert channels and phone call SOS signals.",
            "price": 99.99,
            "billing_cycle": "monthly",
            "max_users": 9999,
            "max_devices": 9999,
            "alert_type": "phone_call",
            "features": [
                "All Professional features",
                "Full real-time monitoring (malware, unregistered devices, anomalies)",
                "Custom alert rules per department",
                "SOS Phone alerts (auto call)",
                "Dedicated support manager"
            ],
        },
    ]

    for plan_data in plans:
        plan = Subscription.query.filter_by(name=plan_data["name"]).first()
        if plan:
            # Update existing plan
            plan.description = plan_data["description"]
            plan.price = plan_data["price"]
            plan.billing_cycle = plan_data["billing_cycle"]
            plan.max_users = plan_data["max_users"]
            plan.max_devices = plan_data["max_devices"]
            plan.alert_type = plan_data["alert_type"]
            plan.features = plan_data["features"]
            print(f"🔄 Updated existing plan: {plan.name}")
        else:
            # Create new plan
            plan = Subscription(**plan_data)
            db.session.add(plan)
            print(f"🆕 Created new plan: {plan.name}")

    db.session.commit()
    print("✅ Subscription plans seeded successfully.")


# =========================================================
# 🏫 Default Organization (optional)
# =========================================================
def seed_org():
    org = Organization.query.filter_by(name="TenshiGuard Academy").first()
    if org:
        print("✔ Organization already exists — skipping.")
        return org

    org = Organization(
        name="TenshiGuard Academy",
        sector="Academic",
        location="Canada",
        total_users=0,
        total_devices=0,
        is_paid=False,
        status="lead"
    )
    db.session.add(org)
    db.session.commit()
    print("✅ Default organization created successfully.")
    return org


# =========================================================
# 👤 Default Admin (optional)
# =========================================================
def seed_admin(org):
    admin = User.query.filter_by(email="admin@tenshiguard.com").first()
    if admin:
        print("✔ Admin user already exists — skipping.")
        return

    admin = User(
        username="admin",
        email="admin@tenshiguard.com",
        role="admin",
        sector="Academic",
        organization_id=org.id,
    )
    admin.set_password("Admin@2025")
    db.session.add(admin)
    db.session.commit()
    print("✅ Admin account created: admin@tenshiguard.com / Admin@2025")


# =========================================================
# 🧠 Main Runner
# =========================================================
if __name__ == "__main__":
    with app.app_context():
        print("\n🚀 Starting TenshiGuard Database Seeding...\n")
        seed_subscriptions()

        org = seed_org()
        seed_admin(org)

        print("\n🎉 TenshiGuard Database Seeding Complete!\n")
        print("🔑 Test Admin Login:")
        print("   Email: admin@tenshiguard.com")
        print("   Password: Admin@2025\n")
        print("------------------------------------------------------")
        print("If you make schema changes, run:")
        print("   flask db upgrade && python3 create_seed_data.py")
        print("------------------------------------------------------")
