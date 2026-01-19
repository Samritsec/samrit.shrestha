import textwrap
import base64
import ast
import sys

# Mock variables
class Org:
    agent_token = "TEST_TOKEN"
org = Org()
base = "http://localhost:5000"

# Mock watchdog for syntax check context if needed (though syntax check doesn't run imports)
# But let's add it to be safe if we were running it.
sys.modules['watchdog'] = type('watchdog', (), {'observers': type('observers', (), {'Observer': object}), 'events': type('events', (), {'FileSystemEventHandler': object})})


# Extracted logic from agent_installer.py
try:
    client_py = textwrap.dedent(f"""\
        #!/usr/bin/env python3
        \"\"\"TenshiGuard unified Agent (Linux/Windows/macOS)
        - Registers device
        - Sends heartbeats every 2s (Real-time)
        - Streams login/logout events immediately
        \"\"\"
        import os, time, socket, uuid, threading, subprocess, platform, shutil, sys
        from datetime import datetime, timezone

        import requests
        try:
            import psutil
        except ImportError:
            psutil = None

        SERVER = "{base}"
        ORG_TOKEN = "{org.agent_token}"
        HEARTBEAT_INTERVAL = 2  # Real-time feedback

        # ------------------ Helpers ------------------
        def log(msg):
            now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
            print(f"[agent] {{now}} :: {{msg}}", flush=True)

        def mac_address():
            try:
                mac = uuid.getnode()
                parts = []
                for ele in range(40, -8, -8):
                    parts.append(f"{{(mac >> ele) & 0xff:02x}}")
                return ":".join(parts)
            except Exception:
                return "unknown"

        def get_ip():
            # Best-effort outward IP
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                ip = s.getsockname()[0]
                s.close()
                return ip
            except Exception:
                try:
                    return socket.gethostbyname(socket.gethostname())
                except Exception:
                    return "0.0.0.0"

        def system_info():
            return {{
                "hostname": platform.node(),
                "os": f"{{platform.system()}} {{platform.release()}}",
                "ip": get_ip(),
                "mac": mac_address(),
            }}

        def post(path, payload):
            url = f"{{SERVER}}{{path}}"
            try:
                r = requests.post(url, json=payload, timeout=2) # Fast timeout for real-time
                return r.status_code, r.text
            except Exception as e:
                # log(f"post error: {{e}}") # Reduce noise
                return 0, str(e)

        # -------------- Metrics ----------------
        def gather_stats():
            cpu = mem = 0.0
            if psutil:
                try:
                    cpu = psutil.cpu_percent(interval=None) # Non-blocking
                    mem = psutil.virtual_memory().percent
                except Exception:
                    cpu = mem = 0.0
            return cpu, mem

        # -------------- API calls --------------
        def register():
            info = system_info()
            cpu, mem = gather_stats()
            payload = {{
                "org_token": ORG_TOKEN,
                "hostname": info["hostname"],
                "mac": info["mac"],
                "os": info["os"],
                "ip": info["ip"],
                "cpu_percent": cpu,
                "mem_percent": mem,
                "agent_version": "1.0.0",
                "ts": datetime.now(timezone.utc).isoformat(),
            }}
            code, body = post("/api/agent/register", payload)
            log(f"register -> {{code}}")
            return code

        def heartbeat():
            info = system_info()
            cpu, mem = gather_stats()
            payload = {{
                "org_token": ORG_TOKEN,
                "hostname": info["hostname"],
                "mac": info["mac"],
                "os": info["os"],
                "ip": info["ip"],
                "cpu_percent": cpu,
                "mem_percent": mem,
                "status": "online",
                "agent_version": "1.0.0",
                "ts": datetime.now(timezone.utc).isoformat(),
            }}
            code, body = post("/api/agent/heartbeat", payload)
            # log(f"heartbeat -> {{code}}") # Too noisy for 2s
            return code

        def send_event(category, action, detail, severity="medium"):
            info = system_info()
            payload = {{
                "org_token": ORG_TOKEN,
                "mac": info["mac"],
                "category": category,
                "action": action,
                "detail": detail,
                "severity": severity,
                "ts": datetime.now(timezone.utc).isoformat(),
            }}
            # UPDATED: Send to the AI ingest endpoint which handles generic events too
            code, body = post("/api/agent/ai/event", payload)
            log(f"event({{category}}/{{action}}) -> {{code}}")
            return code

        # -------------- Network Intrusion Detection (Reverse Shells / Bad Ports) --------------
        def monitor_network():
            \"\"\"Scans for suspicious network connections (Reverse Shells, Bad Ports).\"\"\"
            SUSPICIOUS_PORTS = [4444, 1337, 6667, 31337, 12345]
            SHELL_PROCESSES = ["cmd.exe", "powershell.exe", "bash", "sh", "nc.exe", "ncat.exe"]
            
            log("Starting Network Monitor (Interval: 60s)...")
            
            seen_connections = set() # hash of pid+ip+port

            while True:
                try:
                    current_conns = set()
                    if psutil:
                        # Scan all inet connections
                        for conn in psutil.net_connections(kind='inet'):
                            try:
                                if conn.status != 'ESTABLISHED':
                                    continue
                                    
                                pid = conn.pid
                                if not pid: continue
                                
                                proc = psutil.Process(pid)
                                name = (proc.name() or "").lower()
                                
                                raddr = conn.raddr
                                if not raddr: continue
                                
                                remote_ip, remote_port = raddr
                                
                                # Ignore local/private IPs (simple check)
                                if remote_ip.startswith("127.") or remote_ip.startswith("192.168.") or remote_ip.startswith("10."):
                                    continue
                                    
                                conn_id = f"{{pid}}-{{remote_ip}}-{{remote_port}}"
                                current_conns.add(conn_id)
                                
                                if conn_id in seen_connections:
                                    continue

                                # 1. Check Bad Ports
                                if remote_port in SUSPICIOUS_PORTS:
                                    msg = f"Suspicious outbound connection to port {{remote_port}} from {{name}} (PID: {{pid}})"
                                    log(msg)
                                    send_event("network", "suspicious_port", msg, "high")
                                    seen_connections.add(conn_id)
                                    continue

                                # 2. Check Reverse Shells (Shell process connecting to internet)
                                if name in SHELL_PROCESSES:
                                    msg = f"Reverse Shell Detected: {{name}} connected to {{remote_ip}}:{{remote_port}}"
                                    log(msg)
                                    send_event("network", "reverse_shell", msg, "critical")
                                    seen_connections.add(conn_id)

                            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                                pass
                    
                    # Cleanup seen_connections
                    seen_connections = seen_connections.intersection(current_conns)

                except Exception as e:
                    log(f"Network monitor error: {{e}}")
                
                time.sleep(60)

        # -------------- Auth Monitoring (Cross-Platform) --------------
        
        def tail_linux_auth():
            \"\"\"Stream journald or auth.log for Linux\"\"\"
            cmd = None
            source = None

            if shutil.which("journalctl"):
                cmd = ["journalctl", "-f", "-n", "0", "-u", "ssh", "-u", "sshd", "_COMM=sshd", "_COMM=login", "_COMM=sudo"]
                source = "journald"
            elif os.path.exists("/var/log/auth.log"):
                cmd = ["tail", "-n", "0", "-F", "/var/log/auth.log"]
                source = "/var/log/auth.log"
            elif os.path.exists("/var/log/secure"): # RHEL/CentOS
                cmd = ["tail", "-n", "0", "-F", "/var/log/secure"]
                source = "/var/log/secure"

            if not cmd:
                log("No auth log source found (journald/auth.log/secure).")
                return

            log(f"Watching {{source}} for auth events...")
            try:
                proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                
                # Keywords for detection
                fail_patterns = ["Failed password", "authentication failure", "Invalid user"]
                success_patterns = ["Accepted password", "session opened for user"]
                logout_patterns = ["session closed for user", "pam_unix(sshd:session): session closed"]

                for line in iter(proc.stdout.readline, ""):
                    line = line.strip()
                    if not line: continue

                    if any(p in line for p in fail_patterns):
                        send_event("auth", "failed_login", line, "medium")
                    elif any(p in line for p in success_patterns):
                        send_event("auth", "login", line, "info")
                    elif any(p in line for p in logout_patterns):
                        send_event("auth", "logout", line, "info")
            except Exception as e:
                log(f"Linux auth watcher failed: {{e}}")

        def is_admin():
            try:
                if platform.system().lower() == 'windows':
                    import ctypes
                    return ctypes.windll.shell32.IsUserAnAdmin() != 0
                else:
                    return os.geteuid() == 0
            except:
                return False

        def tail_windows_events():
            '''Stream Windows Event Log via PowerShell (Robust RecordId Tailing)'''
            if not is_admin():
                log("Running as non-admin: Windows Security Log monitoring disabled.")
                return

            log("Watching Windows Security Event Log (RecordId Tailing)...")
            
            # 1. Get initial baseline (latest event RecordId)
            # Get-WinEvent -LogName Security -FilterXPath "*[System[(EventID=4624 or EventID=4625 or EventID=4647)]]" -MaxEvents 1 -ErrorAction SilentlyContinue | Select-Object RecordId | ConvertTo-Json
            startup_b64 = "RwBlAHQALQBXAGkAbgBFAHYAZQBuAHQAIAAtAEwAbwBnAE4AYQBtAGUAIABTAGUAYwB1AHIAaQB0AHkAIAAtAEYAaQBsAHQAZQByAFgAUABhAHQAaAAgACIAKgBbAFMAeQBzAHQAZQBtAFsAKABFAHYAZQBuAHQASQBEAD0ANAA2ADIANAAgAG8AcgAgAEUAdgBlAG4AdABJAEQAPQA0ADYAMgA1ACAAbwByACAARQB2AGUAbgB0AEkARAA9ADQANgA0ADcAKQBdAF0AIgAgAC0ATQBhAHgARQB2AGUAbgB0AHMAIAAxACAALQBFAHIAcgBvAHIAQQBjAHQAaQBvAG4AIABTAGkAbABlAG4AdABsAHkAQwBvAG4AdgBlAHIAdABUAG8ALQBKAHMAbwBuAA=="
            
            last_record_id = 0
            try:
                out = subprocess.check_output(["powershell", "-EncodedCommand", startup_b64], text=True).strip()
                if out:
                    import json
                    try:
                        data = json.loads(out)
                        if isinstance(data, dict):
                            last_record_id = int(data.get("RecordId", 0))
                        elif isinstance(data, list) and len(data) > 0:
                            last_record_id = int(data[0].get("RecordId", 0))
                    except:
                        pass
            except:
                pass
                
            log(f"Starting event tail from RecordId > {{last_record_id}}")

            # 2. Polling Loop
            # Get-WinEvent -LogName Security -FilterXPath "*[System[(EventID=4624 or EventID=4625 or EventID=4647)]]" -MaxEvents 10 -ErrorAction SilentlyContinue | Select-Object RecordId, Id, Message, TimeCreated | ConvertTo-Json
            poll_b64 = "RwBlAHQALQBXAGkAbgBFAHYAZQBuAHQAIAAtAEwAbwBnAE4AYQBtAGUAIABTAGUAYwB1AHIAaQB0AHkAIAAtAEYAaQBsAHQAZQByAFgAUABhAHQAaAAgACIAKgBbAFMAeQBzAHQAZQBtAFsAKABFAHYAZQBuAHQASQBEAD0ANAA2ADIANAAgAG8AcgAgAEUAdgBlAG4AdABJAEQAPQA0ADYAMgA1ACAAbwByACAARQB2AGUAbgB0AEkARAA9ADQANgA0ADcAKQBdAF0AIgAgAC0ATQBhAHgARQB2AGUAbgB0AHMAIAAxADAAIAAtAEUAcgByAG8AcgBBAGMAdABpAG8AbgAgAFMAaQBsAGUAbgB0AGwAeQBDAG8AbgB0AGkAbgB1AGUAIAB8ACAAUwBlAGwAZQBjAHQALQBPAGIAagBlAGMAdAAgAFIAZQBjAG8AcgBkAEkAZAAsACAASQBkACwAIABNAGUAcwBzAGEAZwBlACwAIABUAGkAbQBlAEMAcgBlAGEAdABlAGQAIAB8ACAAQwBvAG4AdgBlAHIAdABUAG8ALQBKAHMAbwBuAA=="
            cmd = ["powershell", "-EncodedCommand", poll_b64]

            while True:
                try:
                    out = subprocess.check_output(cmd, text=True).strip()
                    if out:
                        import json
                        try:
                            data = json.loads(out)
                            if isinstance(data, dict): data = [data]
                            
                            # Sort by RecordId ascending to process in order
                            data.sort(key=lambda x: x.get("RecordId", 0))

                            for event in data:
                                rid = int(event.get("RecordId", 0))
                                if rid <= last_record_id:
                                    continue
                                
                                last_record_id = rid
                                eid = event.get("Id")
                                msg = event.get("Message", "")[:200]
                                
                                if eid == 4624:
                                    if "Advapi" not in msg and "SYSTEM" not in msg: 
                                        send_event("auth", "login", f"Windows Logon: {{msg}}", "info")
                                elif eid == 4625:
                                    send_event("auth", "failed_login", f"Windows Failed Logon: {{msg}}", "medium")
                                elif eid == 4647:
                                    send_event("auth", "logout", f"Windows Logoff: {{msg}}", "info")
                                    
                        except json.JSONDecodeError:
                            pass
                except subprocess.CalledProcessError:
                    pass
                    
                time.sleep(2)

        def start_auth_watcher():
            sys_plat = platform.system().lower()
            if "linux" in sys_plat or "darwin" in sys_plat: # macOS is similar to Linux (uses unified log, but tailing works for some things)
                # For macOS specifically, 'log stream' is better, but let's stick to linux tail for now as fallback
                # If macOS, we might need a specific handler.
                if "darwin" in sys_plat:
                    # macOS 'log stream' TODO
                    pass 
                else:
                    threading.Thread(target=tail_linux_auth, daemon=True).start()
            elif "windows" in sys_plat:
                threading.Thread(target=tail_windows_events, daemon=True).start()

        # -------------- Main loop --------------
        def main():
            log(f"Starting TenshiGuard Agent v1.0.0 on {{platform.system()}}...")
            
            # Initial Register
            code = register()
            if code not in (200, 201):
                log("Initial register failed; will retry in loop")

            # Start Event Monitoring
            start_auth_watcher()

            # Heartbeat Loop
            while True:
                code = heartbeat()
                if code == 404:
                    log("Heartbeat 404: Device not found. Re-registering...")
                    register()
                
                time.sleep(HEARTBEAT_INTERVAL)

        if __name__ == "__main__":
            main()
    """)

    print("[OK] Generation Successful!")
    
    # Verify Syntax
    try:
        ast.parse(client_py)
        print("[OK] Python Syntax Valid!")
    except SyntaxError as e:
        print(f"[FAIL] Python Syntax Error: {e}")
        exit(1)

    # Verify Base64
    # (Optional: decode and print to check)
    
except Exception as e:
    print(f"[FAIL] Generation Failed: {e}")
    exit(1)
