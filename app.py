from flask import Flask, request, abort
import smtplib
from email.mime.text import MIMEText
import ssl
import hmac
import hashlib

app = Flask(__name__)

# Jouw HMAC-secret
HMAC_SECRET = b"wsec_a5adb70ff267065fc290c5b42b0fee583bbe448107fa4d6e26074610e7b1ca5a"

@app.route('/transcript', methods=['POST'])
def send_transcript():
    # Verifieer HMAC-handtekening
    signature = request.headers.get('X-Webhook-Signature', '')
    body = request.get_data()

    expected_signature = hmac.new(HMAC_SECRET, body, hashlib.sha256).hexdigest()

    if not hmac.compare_digest(expected_signature, signature):
        print("Ongeldige HMAC-signature")
        abort(401, description="Invalid signature")

    # Verwerk de inkomende data
    data = request.json
    transcript = data.get('transcript', 'Geen transcript ontvangen.')
    naam = data.get('naam', 'Onbekend')
    telefoonnummer = data.get('telefoonnummer', 'Onbekend')
    email = data.get('email', 'Onbekend')

    # Stel de HTML-email samen
    html_content = f"""
    <html>
        <body>
            <h2>Nieuwe AI-gesprek binnengekomen!</h2>
            <p><strong>Naam:</strong> {naam}</p>
            <p><strong>Telefoonnummer:</strong> {telefoonnummer}</p>
            <p><strong>E-mailadres:</strong> {email}</p>
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
        print(f"Fout bij verzenden: {e}")
        return f"Fout: {e}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
