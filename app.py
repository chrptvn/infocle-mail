import os
import re
import smtplib
from email.message import EmailMessage
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()

# --- Configuration from environment ---
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))  # TLS
GMAIL_USER = os.getenv("GMAIL_USER")            # your Gmail address
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")  # 16-char app password
TO_EMAIL = os.getenv("TO_EMAIL", GMAIL_USER)    # where to receive form mail

app = Flask(__name__)

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

def is_valid_email(value: str) -> bool:
    return bool(value and EMAIL_RE.match(value))

@app.post("/api/v1/send_mail")
def send_mail():
    # Accept JSON or form-encoded payloads
    data = request.get_json(silent=True) or request.form

    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip()
    subject = (data.get("subject") or "Website contact").strip()
    message = (data.get("message") or "").strip()
    # Simple anti-bot honeypot: leave this field empty in your form
    honeypot = (data.get("company") or "").strip()

    # Basic validation
    if honeypot:
        return jsonify({"ok": True}), 200  # silently ignore bots
    if not name or not message or not is_valid_email(email):
        return jsonify({"ok": False, "error": "Invalid input"}), 400

    # Build email
    msg = EmailMessage()
    msg["Subject"] = f"[Contact] {subject}"
    msg["From"] = f"{name} <{GMAIL_USER}>"          # authenticated sender
    msg["Reply-To"] = f"{name} <{email}>"           # user who filled the form
    msg["To"] = TO_EMAIL

    body = (
        f"New contact form submission\n\n"
        f"Name: {name}\n"
        f"Email: {email}\n"
        f"Subject: {subject}\n"
        f"Message:\n{message}\n"
    )
    msg.set_content(body)

    # Send via Gmail SMTP (TLS)
    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=20) as smtp:
            smtp.ehlo()
            smtp.starttls()  # upgrade connection to TLS
            smtp.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            smtp.send_message(msg)
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 502

    return jsonify({"ok": True}), 200
