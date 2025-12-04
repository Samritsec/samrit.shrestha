import requests

def verify_dashboard():
    session = requests.Session()
    base_url = "http://127.0.0.1:5003"

    # 1. Login
    print("Logging in...")
    resp = session.post(f"{base_url}/login", data={
        "email": "testorg1@gmail.com",
        "password": "12345678@Testorg"
    })
    
    if resp.status_code != 200:
        print(f"Login failed: {resp.status_code}")
        return

    # 2. Fetch API Data
    print("Fetching API Data...")
    
    # Top Devices
    resp_devices = session.get(f"{base_url}/api/dashboard/top-devices")
    if resp_devices.status_code != 200:
        print(f"Devices API failed: {resp_devices.status_code}")
    else:
        devices_data = resp_devices.json()
        # print(f"Devices API Response: {devices_data}")
        
        # Verify Simulated-PC
        found = any(d.get('device_name') == 'Simulated-PC' for d in devices_data.get('items', []))
        if found:
            print("✅ 'Simulated-PC' found in API response.")
        else:
            print("❌ 'Simulated-PC' NOT found in API response.")

    # Summary
    resp_summary = session.get(f"{base_url}/api/dashboard/summary")
    if resp_summary.status_code != 200:
        print(f"Summary API failed: {resp_summary.status_code}")
    else:
        summary_data = resp_summary.json()
        # print(f"Summary API Response: {summary_data}")
        
        events_count = summary_data.get('events', {}).get('last_24h', 0)
        print(f"Events (24h): {events_count}")
        
        if events_count > 0:
             print("✅ Events count is positive (Live Data).")
        else:
             print("❌ Events count is zero.")

    print("-" * 30)

if __name__ == "__main__":
    verify_dashboard()
