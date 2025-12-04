import random
from datetime import datetime, timezone
from app.extensions import db
from app.models.alert import Alert

class LearningEngine:
    """
    🧠 Adaptive AI Engine
    Handles user feedback (True/False Positives) to adjust rule confidence scores
    and simulates fetching global threat intelligence.
    """

    def submit_feedback(self, alert_id, feedback_type):
        """
        Process user feedback for a specific alert (Event).
        feedback_type: 'true_positive' | 'false_positive'
        """
        from app.models.ai_learned_rule import AILearnedRule
        from app.models.event import Event

        # Query Event instead of Alert
        event = Event.query.get(alert_id)
        if not event:
            return False, "DEBUG: Event not found (ID mismatch?)"

        event.feedback = feedback_type
        event.feedback_at = datetime.now(timezone.utc)
        
        # Adjust score based on feedback
        if feedback_type == 'false_positive':
            event.adjusted_score = 0.1  # Deprioritize
        else:
            event.adjusted_score = 1.0  # Reinforce

        # ------------------------------------------------
        # 🧠 Continuous Learning: Update Rule Weights
        # ------------------------------------------------
        # Extract rule name from message if possible, or use category
        # Message format: "RuleName — Severity" or similar
        rule_name = "unknown"
        if event.message and "—" in event.message:
            rule_name = event.message.split("—")[0].strip()
        elif event.category:
            rule_name = event.category

        if rule_name:
            learned_rule = AILearnedRule.query.filter_by(rule_name=rule_name).first()
            if not learned_rule:
                learned_rule = AILearnedRule(rule_name=rule_name, weight_modifier=0.0, feedback_count=0)
                db.session.add(learned_rule)
            
            if feedback_type == 'true_positive':
                learned_rule.weight_modifier += 5.0
            elif feedback_type == 'false_positive':
                learned_rule.weight_modifier -= 10.0
            
            # Cap the modifier to avoid extreme skew
            learned_rule.weight_modifier = max(-50.0, min(50.0, learned_rule.weight_modifier))
            
            learned_rule.feedback_count += 1
            learned_rule.last_updated = datetime.now(timezone.utc)

        db.session.commit()
        return True, "Feedback recorded"

    def get_training_stats(self, org_id):
        """
        Calculate model accuracy based on user feedback.
        """
        from app.models.event import Event
        
        total_feedback = Event.query.filter_by(organization_id=org_id).filter(Event.feedback != None).count()
        if total_feedback == 0:
            return {
                "accuracy": 0,
                "true_positives": 0,
                "false_positives": 0,
                "total_learned": 0
            }

        true_positives = Event.query.filter_by(organization_id=org_id, feedback='true_positive').count()
        false_positives = Event.query.filter_by(organization_id=org_id, feedback='false_positive').count()
        
        accuracy = int((true_positives / total_feedback) * 100)

        return {
            "accuracy": accuracy,
            "true_positives": true_positives,
            "false_positives": false_positives,
            "total_learned": total_feedback
        }

    def fetch_global_threats(self):
        """
        Simulate fetching real-time threat intelligence from the web.
        """
        threats = [
            {"type": "Ransomware", "name": "LockBit 3.0", "trend": "High", "region": "Global"},
            {"type": "Phishing", "name": "AiTM Attacks", "trend": "Critical", "region": "North America"},
            {"type": "Malware", "name": "QakBot Resurgence", "trend": "Medium", "region": "Europe"},
            {"type": "Exploit", "name": "CVE-2025-1337 (Zero-Day)", "trend": "Critical", "region": "Global"},
            {"type": "Botnet", "name": "Mirai Variant X", "trend": "Low", "region": "Asia"}
        ]
        # Shuffle to simulate "live" updates
        random.shuffle(threats)
        return threats[:3]
