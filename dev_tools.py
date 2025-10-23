import subprocess
import sys
import threading
import click
import socket
from app import create_app

# Initialize the Flask app
app = create_app()

def run_smtp():
    """Run a local debug SMTP server that prints all emails to console."""
    sock = socket.socket()
    sock.bind(("localhost", 0))
    port = sock.getsockname()[1]
    sock.close()
    click.echo(f"📧 Starting fake SMTP server on localhost:{port} ...")
    subprocess.run([sys.executable, "-m", "aiosmtpd", "-n", "-l", f"localhost:{port}"])
    
@app.cli.command("maildebug")
@click.option("--open", is_flag=True, help="Automatically open the app in your browser.")
def maildebug(open):
    """
    Start the TenshiGuard Flask app + local debug mail server (Python 3.12+ safe).
    Usage: flask maildebug
    """
    import webbrowser

    # Start the SMTP server in a background thread
    thread = threading.Thread(target=run_smtp, daemon=True)
    thread.start()

    click.echo("🚀 TenshiGuard Flask app starting at http://127.0.0.1:5000")

    # Optional: Auto-open browser
    if open:
        webbrowser.open("http://127.0.0.1:5000/login")

    # ✅ No app.run() — Flask CLI handles that automatically
