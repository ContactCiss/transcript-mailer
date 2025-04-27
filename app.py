from flask import Flask, request, abort
import smtplib
from email.mime.text import MIMEText
import ssl
import hmac
import hashlib

app = Flask(__name__)

# HMAC secret
HMAC_SECRET = b"wsec_733a441c67f6b5ac1f042e922472a07a3aaf9ce9349bc3d97b156f798f708bf6"

@app.route('/transcript', methods=['POST'])
def send_transcript():
    print("\n🛬 Webhook POST ontvangen!")

    signature = request.headers.get('X-Webhook-Signature', '')
    body = request.get_data()

    print(f"📩 Raw body (bytes): {body}")
    print(f"📩 Raw body (decoded): {body.decode('utf-8', errors='replace')}")
    print(f"🧩 Ontvangen X-Webhook-Signature header: {signature}")

    expected_signature = hmac.new(HMAC_SECRET, body, hashlib.sha256).hexdigest()

    print(f"✅ Verwachte HMAC: {expected_signature}")

    if not hmac.compare_digest(expected_signature, signature):
        print("🚫 Ongeldige HMAC-signature! Webhook geweigerd.")
        abort(401, description="Invalid signature")

    print("✅ HMAC signature geldig. E-mail wordt verstuurd.")

    # JSON parsen
    try:
        data = request.get_json()
        print(f"📦 JSON payload: {data}")
    except Exception as e:
        print(f"🚫 Fout bij JSON parsing: {e}")
        abort(400, description="Invalid JSON")

    transcript = data.get('transcript', 'Geen transcript ontvangen.')

    html_content = f"""
    <html>
        <body>
            <h2>Nieuwe AI-gesprek binnengekomen!</h2>
            <p><strong>Bericht:</strong><br>{transcript}</p>
        </body>
    </html>
    """

    msg = MIMEText(html_content, 'html')
    msg['Subject'] = 'Nieuwe transcriptie van AI gesprek'
    msg['From'] = 'support@contactons.nl'
    msg['To'] = 'support@contactons.nl'

    context = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL('mail.contactons.nl', 465, context=context) as server:
            server.login('support@contactons.nl', 'SuPP#2123(CO')
            server.send_message(msg)
        return 'Transcript verstuurd', 200
    except Exception as e:
        print(f"🚫 Fout bij verzenden: {e}")
        return f"Fout: {e}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
