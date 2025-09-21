import os
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

def send_email(subject: str, body: str) -> tuple[bool, str]:
    """
    Generic email sender function.
    
    Args:
        subject: Email subject line
        body: Email body content
        
    Returns:
        tuple: (success: bool, error_message: str)
    """
    try:
        # Build email
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = GMAIL_USER
        msg["To"] = TO_EMAIL
        msg.set_content(body)

        # Send via Gmail SMTP (TLS)
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=20) as smtp:
            smtp.ehlo()
            smtp.starttls()  # upgrade connection to TLS
            smtp.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            smtp.send_message(msg)
            
        return True, ""
        
    except Exception as e:
        return False, str(e)

@app.post("/api/v1/send_mail")
def send_mail():
    """
    API endpoint to send mail from web forms.
    Accepts subject and body in JSON or form data.
    """
    # Accept JSON or form-encoded payloads
    data = request.get_json(silent=True) or request.form

    subject = (data.get("subject") or "Website Contact").strip()
    body = (data.get("body") or "").strip()
    
    # Simple anti-bot honeypot: leave this field empty in your form
    honeypot = (data.get("honeypot") or "").strip()

    # Basic validation
    if honeypot:
        return jsonify({"ok": True}), 200  # silently ignore bots
    if not body:
        return jsonify({"ok": False, "error": "Body is required"}), 400

    # Send email using generic function
    success, error = send_email(subject, body)
    
    if success:
        return jsonify({"ok": True}), 200
    else:
        return jsonify({"ok": False, "error": error}), 502

@app.route("/health")
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy"}), 200

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)