import requests
import json
import time

# Configuration
API_URL = "http://localhost:5001/api/agent/ai/event"
ORG_TOKEN = "tg-admin-token" # Valid token from database
MAC_ADDRESS = "00:11:22:33:44:55"

def send_event(severity="high"):
    payload = {
        "org_token": ORG_TOKEN,
        "mac": MAC_ADDRESS,
        "hostname": "risk-test-device",
        "os": "windows",
        "ip": "192.168.1.100",
        "type": "process",
        "process_name": "mimikatz.exe",
        "description": "Simulated risk test",
        "severity": severity # This might be overridden by AI engine if it analyzes the payload
    }
    
    # Note: The AI engine analyzes the payload. To force a severity, we might need to match a rule.
    # Or we can rely on the fact that 'mimikatz.exe' should trigger a high/critical rule if the engine is active.
    
    try:
        resp = requests.post(API_URL, json=payload)
        print(f"Sent event: {resp.status_code} - {resp.text}")
        return resp.json()
    except Exception as e:
        print(f"Error sending event: {e}")
        return None

if __name__ == "__main__":
    print("Sending High Severity Event...")
    send_event()
    print("Check dashboard or database for risk score update.")
