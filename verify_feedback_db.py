from app import create_app, db
from app.models.alert import Alert

app = create_app()
with app.app_context():
    # Check for specific feedback types
    true_pos = Alert.query.filter_by(feedback='true_positive').count()
    false_pos = Alert.query.filter_by(feedback='false_positive').count()
    
    print(f"True Positives: {true_pos}")
    print(f"False Positives: {false_pos}")
    
    if true_pos > 0:
        alert = Alert.query.filter_by(feedback='true_positive').order_by(Alert.feedback_at.desc()).first()
        print(f"Latest True Positive: {alert.title} at {alert.feedback_at}")

